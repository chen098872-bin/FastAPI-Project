# 修正导入：AsyncSession 来自 sqlalchemy.ext.asyncio
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history_test import NameHistory


class NameHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 保存生成记录（原方法不变，正确）
    async def create(
        self,
        user_id: int,
        input_params: dict,
        generated_names: dict,
        model_used: str
    ) -> NameHistory:
        async with self.session.begin():
            history = NameHistory(
                user_id=user_id,
                input_params=input_params,
                generated_names=generated_names,
                model_used=model_used
            )
            self.session.add(history)
            return history

    # 查询用户的历史记录（原方法不变，正确）
    async def get_by_user(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> List[NameHistory]:
        async with self.session.begin():
            offset = (page - 1) * page_size
            stmt = select(NameHistory).filter(
                NameHistory.user_id == user_id
            ).order_by(
                NameHistory.created_at.desc()
            ).limit(page_size).offset(offset)
            result = await self.session.execute(stmt)
            return result.scalars().all()

    # 修复：单条删除历史记录（实例方法，添加 self 参数，使用 user_id 而非 User 对象）
    async def delete_single_history(
        self,
        history_id: int,
        user_id: int  # 接收 user_id（整数），而非 User 对象
    ) -> bool:
        """
        删除单条历史记录
        - 验证记录存在且属于当前用户
        - 返回：成功返回 True，失败返回 False
        """
        async with self.session.begin():  # 统一事务管理
            # 查询记录并验证归属
            stmt = select(NameHistory).where(
                NameHistory.id == history_id,
                NameHistory.user_id == user_id
            )
            result = await self.session.execute(stmt)
            history = result.scalars().first()
            if not history:
                return False

            # 删除记录（事务内自动提交）
            await self.session.delete(history)
            return True

    # 修复：批量删除历史记录（实例方法，添加 self 参数，使用 user_id 而非 User 对象）
    async def delete_batch_history(
        self,
        history_ids: List[int],
        user_id: int  # 接收 user_id（整数），而非 User 对象
    ) -> int:
        """
        批量删除历史记录
        - 仅删除属于当前用户的记录
        - 返回：成功删除的记录数量
        """
        async with self.session.begin():  # 统一事务管理
            # 执行批量删除（带条件：ID在列表中且属于当前用户）
            stmt = delete(NameHistory).where(
                NameHistory.id.in_(history_ids),
                NameHistory.user_id == user_id
            )
            result = await self.session.execute(stmt)
            # 事务内自动提交，返回删除的行数
            return result.rowcount