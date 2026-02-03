"""
应用配置模块
管理所有配置项，支持环境变量覆盖
"""

import os
import secrets
from pathlib import Path
from typing import Set
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # 兼容旧版本Pydantic
    from pydantic import BaseSettings

from pydantic import validator


class Settings(BaseSettings):
    """应用配置类"""

    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent

    # 静态文件目录
    STATIC_DIR: Path = BASE_DIR / "static"

    # 头像存储目录
    AVATAR_DIR: Path = STATIC_DIR / "avatars"

    # API配置
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_WORKERS: int = 1

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = False

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "llm_chat"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_ECHO: bool = False

    # AI服务配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_TEMPERATURE: float = 1.2
    DEEPSEEK_MAX_TOKENS: int = 2000
    DEEPSEEK_TIMEOUT: int = 120

    ALIBABA_API_KEY: str = ""
    ALIBABA_MODEL: str = "qwen-plus"
    ALIBABA_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ALIBABA_TEMPERATURE: float = 1.2
    ALIBABA_TIMEOUT: int = 120

    # 姓名测评超时时间（秒）
    NAME_EVALUATION_TIMEOUT: int = 300

    # AI重试配置
    AI_MAX_RETRIES: int = 3
    AI_RETRY_BACKOFF: float = 1.0

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: Set[str] = {'.png', '.jpg', '.jpeg', '.gif'}

    # 头像访问的基础URL
    AVATAR_BASE_URL: str = f"http://{API_HOST}:{API_PORT}/static/avatars/"

    # JWT配置
    JWT_SECRET_KEY: str = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 * 24 * 60  # 15天
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天

    # 邮件配置
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = ""
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 创建必要的目录
        os.makedirs(self.AVATAR_DIR, exist_ok=True)

        # 如果没有设置SECRET_KEY，生成一个随机的
        if self.SECRET_KEY == "your-secret-key-change-in-production":
            self.SECRET_KEY = secrets.token_hex(32)

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @validator('ALLOWED_EXTENSIONS', pre=True)
    def parse_allowed_extensions(cls, v):
        """解析允许的文件扩展名"""
        if isinstance(v, str):
            return set(v.split(','))
        return v

    @validator('DEBUG', pre=True)
    def parse_debug(cls, v):
        """解析DEBUG配置"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)


# 全局配置实例
settings = Settings()

# 向后兼容的导出（兼容旧代码）
STATIC_DIR = settings.STATIC_DIR
AVATAR_DIR = settings.AVATAR_DIR
AVATAR_BASE_URL = settings.AVATAR_BASE_URL
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT
API_WORKERS = settings.API_WORKERS
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
MAX_UPLOAD_SIZE = settings.MAX_UPLOAD_SIZE
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS