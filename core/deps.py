# 原有基础导入
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from app.core.auth import AuthHandler
from app.core.mail import create_mail_instance
from app.core.config import STATIC_DIR
from app.models import get_db_session
from app.models.user import User


# --------------------------
# 原有依赖：邮件实例（不变）
# --------------------------
async def get_mail() -> FastMail:
    return create_mail_instance()


# --------------------------
# 数据库会话依赖注入
# --------------------------
async def get_session() -> AsyncSession:
    """
    数据库会话依赖注入函数
    使用新的上下文管理器提供安全的数据库会话
    """
    async with get_db_session() as session:
        yield session


# --------------------------
# 新增：认证相关依赖（核心）
# --------------------------
# 实例化认证处理器（单例，全局唯一）
auth_handler = AuthHandler()

# 定义类型注解：简化依赖注入的写法
# 1. 从Token中解析出的用户ID（通过AuthHandler的auth_access_dependency）
UserIDDep = Annotated[int, Depends(auth_handler.auth_access_dependency)]
# 2. 数据库会话的注解（复用原有get_session）
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# --------------------------
# 新增：获取当前登录用户（核心函数）
# --------------------------
async def get_current_user(
    user_id: UserIDDep,  # 从Token解析的用户ID（iss字段）
    db: SessionDep,  # 数据库会话
) -> User:
    """
    依赖逻辑：
    1. 先通过auth_handler解析Token，获取用户ID
    2. 从数据库查询该用户ID对应的用户对象
    3. 若用户不存在，抛出404异常
    """
    # 从数据库查询用户
    user = await db.scalar(select(User).where(User.id == user_id))

    # 用户不存在的异常处理
    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="用户不存在或已被删除"
        )

    # 返回当前用户对象
    return user


# --------------------------
# 新增：简化用户依赖的注解（可选，推荐）
# --------------------------
CurrentUserDep = Annotated[User, Depends(get_current_user)]



# 静态文件服务（FastAPI启动时注册）
def register_static_files(app):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")