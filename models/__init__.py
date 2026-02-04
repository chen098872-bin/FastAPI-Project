"""
数据库模型和连接配置
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.settings import DB_URI

# 配置日志
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    "url": DB_URI,
    # 生产环境禁用SQL日志输出
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
    # 连接池配置
    "poolclass": NullPool if os.getenv("DB_NULL_POOL", "false").lower() == "true" else None,
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    "pool_pre_ping": os.getenv("DB_POOL_PRE_PING", "true").lower() == "true",
    # 连接参数
    "connect_args": {
        "charset": "utf8mb4",
        "autocommit": False,
    }
}

# 创建异步引擎
try:
    engine = create_async_engine(**DB_CONFIG)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# 创建异步会话工厂
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,  # 改为False，更安全
    expire_on_commit=False
)

# 定义Base类
class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类"""
    metadata = MetaData(
        naming_convention={
            "ix": 'ix_%(column_0_label)s',
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话上下文管理器
    提供安全的数据库会话管理，包括错误处理和回滚
    """
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


# 兼容性函数 - 为保持向后兼容
async def get_async_session() -> AsyncSession:
    """
    兼容性函数 - 建议使用 get_db_session() 上下文管理器
    """
    logger.warning("Using deprecated get_async_session(), consider using get_db_session() instead")
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()



from  . import user, history_test, usage, company_naming, product_naming