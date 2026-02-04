from datetime import datetime, timedelta
from typing import Optional, Dict

from sqlalchemy import select, update, delete, exists

from app.models import AsyncSession
from app.models.user import User, EmailCode
from app.models.history_test import NameHistory
from app.schemas.user_schemas import UserCreateSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ===================== 原有方法（完全保留） =====================
    async def get_by_email(self, email: str) -> User | None:
        async with self.session.begin():
            return await self.session.scalar(select(User).filter(User.email == email))

    async def email_is_exist(self, email: str) -> bool:
        async with self.session.begin():
            stmt = select(exists().where(User.email == email))
            return await self.session.scalar(stmt)

    async def create(self, user_schema: UserCreateSchema) -> User:
        async with self.session.begin():
            user = User(** user_schema.model_dump())
            self.session.add(user)
            await self.session.flush()  # 刷新会话，获取用户ID（可选）
            return user

    async def logout_user(self, user_id: int) -> bool:
        """
        注销用户（物理删除）：先删关联数据，再删用户本身
        :param user_id: 当前登录用户ID
        :return: 成功True / 失败False（用户不存在）
        """
        async with self.session.begin():
            # 1. 查询用户是否存在（避免删除不存在的用户）
            user = await self.session.scalar(select(User).filter(User.id == user_id))
            if not user:
                return False

            # 2. 删除用户关联的姓名历史记录（如有）
            await self.session.execute(
                delete(NameHistory).where(NameHistory.user_id == user_id)
            )

            # 3. 删除用户关联的邮箱验证码记录
            await self.session.execute(
                delete(EmailCode).where(EmailCode.email == user.email)
            )

            # 4. 最后删除用户本身
            await self.session.delete(user)  # 直接删除对象更直观（替代execute(delete)）

            return True

    async def get_active_user_by_id(self, user_id: int) -> Optional[User]:
        """物理删除后会返回None，适配原有认证逻辑"""
        async with self.session.begin():
            stmt = select(User).filter(User.id == user_id)
            return await self.session.scalar(stmt)

    # ===================== 新增：支撑编辑资料的方法 =====================
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        别名方法：与get_active_user_by_id逻辑一致，语义更清晰（路由层调用）
        """
        return await self.get_active_user_by_id(user_id)

    async def update_user(self, user: User, update_data: Dict[str, any]) -> User:
        """
        更新用户资料
        :param user: 要更新的用户对象
        :param update_data: 要更新的字段字典（如{"nickname": "新昵称", "gender": "男"}）
        :return: 更新后的用户对象
        """
        async with self.session.begin():
            # 遍历更新字段（仅更新存在的字段）
            for key, value in update_data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            # 提交事务后刷新对象
            await self.session.flush()
            return user

    async def verify_password(self, user_id: int, raw_password: str) -> bool:
        """
        验证用户密码是否正确
        :param user_id: 用户ID
        :param raw_password: 原始密码（前端传入）
        :return: 正确True / 错误False
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        # 调用User模型的check_password方法
        return user.check_password(raw_password)

    async def phone_is_exist(self, phone: str) -> bool:
        """
        检查手机号是否已存在（避免重复绑定）
        :param phone: 手机号
        :return: 存在True / 不存在False
        """
        async with self.session.begin():
            stmt = select(exists().where(User.phone == phone))
            return await self.session.scalar(stmt)


class EmailCodeRepository:
    # 原有方法（完全保留）
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, code: str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            self.session.add(email_code)
            return email_code

    async def check_email_code(self, email: str, code: str) -> bool:
        async with self.session.begin():
            email_code: EmailCode | None = await self.session.scalar(
                select(EmailCode).filter(EmailCode.email == email, EmailCode.code == code))
            if not email_code:
                return False
            # 验证验证码是否过期（10分钟有效期）
            if (datetime.now() - email_code.create_time) > timedelta(minutes=10):
                return False
            return True