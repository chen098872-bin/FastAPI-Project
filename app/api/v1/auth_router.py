import logging
from fastapi import APIRouter, Query, Depends, HTTPException, status, Request
from pydantic import EmailStr
from typing import Annotated, Dict
from fastapi_mail import FastMail, MessageSchema, MessageType
import string
import random
from aiosmtplib import SMTPResponseException

logger = logging.getLogger(__name__)

from app.core.deps import get_mail, get_session, get_current_user
from app.models import AsyncSession
from app.repositories.user_repo import EmailCodeRepository, User, UserRepository
from app.schemas import ResponseOut
from app.schemas.user_schemas import RegisterIn, UserCreateSchema, LoginIn, LoginOut
from app.core.auth import AuthHandler

router = APIRouter(prefix="/auth", tags=["user"])
auth_handler = AuthHandler()


@router.get("/code", response_model=ResponseOut)
async def get_email_code(
        email: Annotated[EmailStr, Query(...)],
        mail: FastMail = Depends(get_mail),
        session: AsyncSession = Depends(get_session),
):
    # 1. 生成4位数字的验证码
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    # 2. 创建消息对象
    message = MessageSchema(
        subject="【llm-chat】注册验证码",
        recipients=[email],
        body=f"您的验证码为：{code}，五分钟有效！",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
        logger.info(f"Email verification code sent successfully to {email}")

        # 将邮箱和验证码存储到数据库中
        email_code_repo = EmailCodeRepository(session=session)
        await email_code_repo.create(str(email), code)

    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            logger.warning(f"Ignoring QQ email SMTP non-standard response for {email} (email sent successfully)")

            # 将邮箱和验证码存储到数据库中
            email_code_repo = EmailCodeRepository(session=session)
            await email_code_repo.create(str(email), code)
        else:
            logger.error(f"SMTP error sending email to {email}: {e}")
            raise HTTPException(500, detail="邮件发送失败！")
    except Exception as e:
        logger.error(f"Unexpected error sending email to {email}: {e}")
        raise HTTPException(500, detail="邮件发送失败！")
    # 适配ResponseOut：仅返回result字段（success）
    return ResponseOut(result="success")


@router.post("/register", response_model=ResponseOut)
async def register(
        data: RegisterIn,
        session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session=session)
    # 1. 判断邮箱是否存在
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(400, detail="该邮箱已经存在！")
    # 2. 校验验证码是否正确（修复：补充await）
    email_code_repo = EmailCodeRepository(session=session)
    email_code_match = await email_code_repo.check_email_code(email=str(data.email), code=str(data.code))
    if not email_code_match:
        raise HTTPException(400, detail='邮箱或验证码错误！')
    try:
        await user_repo.create(UserCreateSchema(email=str(data.email), password=data.password, username=data.username))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    # 适配ResponseOut
    return ResponseOut(result="success")


@router.post('/login')
async def login(
        data: LoginIn,
        session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session=session)
    user: User | None = await user_repo.get_by_email(str(data.email))

    if not user:
        raise HTTPException(400, detail="该用户不存在！")

    if hasattr(user, 'is_deleted') and user.is_deleted:
        raise HTTPException(401, detail="该账号已注销，无法登录！")

    if not user.check_password(data.password):
        raise HTTPException(400, detail="邮箱或密码错误！")

    tokens = auth_handler.encode_login_token(user.id)

    # ✅ 构建完整的用户信息字典
    user_dict = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "nickname": user.nickname if user.nickname else user.username,
        "gender": user.gender if user.gender else "未知",
        "avatar": user.avatar if user.avatar else "",
        "phone": user.phone if user.phone else "",
    }

    # ✅ 添加 avatar_url
    if user.avatar:
        user_dict["avatar_url"] = f"http://127.0.0.1:8000/static/avatars/{user.avatar}"
    else:
        user_dict["avatar_url"] = ""

    return {
        "user": user_dict,
        "token": tokens['access_token']
    }

@router.post("/logout", response_model=ResponseOut)
async def logout(
        request: Request,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)  # 验证用户是否登录
):
    """
    用户登出

    在实际应用中，你可能需要：
    1. 将token加入黑名单（如果使用JWT黑名单机制）
    2. 清除客户端token
    3. 记录登出时间等

    由于JWT是无状态的，通常客户端只需删除本地token即可。
    这个接口主要用于：
    - 验证用户身份
    - 记录登出日志（如果需要）
    - 处理token黑名单（如果实现）
    """

    # 方案1：简单实现 - 只需告知客户端成功登出
    # 客户端应自行删除本地存储的token

    # 方案2：如果需要记录登出时间（更新用户最后登出时间）
    try:
        user_repo = UserRepository(session=session)
        # 如果有last_logout字段，可以更新
        if hasattr(current_user, 'last_logout'):
            await user_repo.update_last_logout(current_user.id)

        # 方案3：如果需要实现token黑名单（需要修改AuthHandler）
        # 获取token并加入黑名单
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # 如果auth_handler支持黑名单功能
            if hasattr(auth_handler, 'add_to_blacklist'):
                await auth_handler.add_to_blacklist(token)

        return ResponseOut(result="success")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )