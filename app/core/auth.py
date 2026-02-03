"""
JWT认证处理模块
遵循RFC 7519标准，实现安全的令牌认证
"""

import jwt
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum
from threading import Lock
from typing import Optional, Dict, Any
import secrets

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app import settings

# 配置日志
logger = logging.getLogger(__name__)


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TokenTypeEnum(str, Enum):
    """令牌类型枚举"""
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"


class AuthHandler(metaclass=SingletonMeta):
    """
    JWT认证处理器
    单例模式，确保全局唯一实例
    """
    security = HTTPBearer(auto_error=False)  # 禁用自动错误，允许自定义处理

    def __init__(self):
        self.secret = settings.JWT_SECRET_KEY
        self.algorithm = 'HS256'
        self.issuer = "llm-chat-api"  # 符合RFC标准的issuer

    def _create_payload(self, user_id: int, token_type: TokenTypeEnum) -> Dict[str, Any]:
        """
        创建符合RFC 7519标准的JWT payload
        """
        now = datetime.now(timezone.utc)
        exp_time = now + (
            settings.JWT_ACCESS_TOKEN_EXPIRES if token_type == TokenTypeEnum.ACCESS_TOKEN
            else settings.JWT_REFRESH_TOKEN_EXPIRES
        )

        payload = {
            # RFC 7519 标准声明
            "iss": self.issuer,  # issuer - 令牌发行者
            "sub": str(user_id),  # subject - 令牌主题（用户ID）
            "iat": int(now.timestamp()),  # issued at - 令牌发行时间
            "exp": int(exp_time.timestamp()),  # expiration - 令牌过期时间
            "jti": secrets.token_hex(16),  # JWT ID - 唯一令牌标识符

            # 自定义声明
            "type": token_type.value,  # 令牌类型
            "version": "1.0"  # API版本
        }

        return payload

    def _encode_token(self, user_id: int, token_type: TokenTypeEnum) -> str:
        """
        编码JWT令牌
        """
        payload = self._create_payload(user_id, token_type)

        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            logger.info(f"Generated {token_type.value} token for user {user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to encode {token_type.value} token for user {user_id}: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="令牌生成失败"
            )

    def encode_login_token(self, user_id: int) -> Dict[str, str]:
        """
        生成登录令牌对（访问令牌 + 刷新令牌）
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(settings.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        }

    def encode_update_token(self, user_id: int) -> Dict[str, str]:
        """
        生成更新令牌（仅访问令牌）
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int(settings.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        }

    def _decode_token(self, token: str, expected_type: TokenTypeEnum) -> int:
        """
        解码并验证JWT令牌

        Args:
            token: JWT令牌字符串
            expected_type: 期望的令牌类型

        Returns:
            用户ID

        Raises:
            HTTPException: 令牌无效或过期
        """
        try:
            # 解码令牌
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "require": ["iss", "sub", "iat", "exp", "jti", "type"]
                }
            )

            # 验证发行者
            if payload.get("iss") != self.issuer:
                logger.warning(f"Invalid issuer in token: {payload.get('iss')}")
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="令牌发行者无效"
                )

            # 验证令牌类型
            if payload.get("type") != expected_type.value:
                logger.warning(f"Token type mismatch. Expected: {expected_type.value}, Got: {payload.get('type')}")
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="令牌类型错误"
                )

            # 验证API版本
            if payload.get("version") != "1.0":
                logger.warning(f"Unsupported token version: {payload.get('version')}")
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="不支持的令牌版本"
                )

            user_id = int(payload["sub"])
            logger.debug(f"Successfully decoded {expected_type.value} token for user {user_id}")

            return user_id

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            status_code = HTTP_401_UNAUTHORIZED if expected_type == TokenTypeEnum.REFRESH_TOKEN else HTTP_403_FORBIDDEN
            raise HTTPException(
                status_code=status_code,
                detail=f"{expected_type.value.replace('_', ' ').title()} Token已过期"
            )
        except jwt.InvalidSignatureError:
            logger.warning("Invalid token signature")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="令牌签名无效"
            )
        except jwt.InvalidIssuerError:
            logger.warning("Invalid token issuer")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="令牌发行者无效"
            )
        except (jwt.InvalidTokenError, KeyError, ValueError) as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="令牌格式无效"
            )

    def decode_access_token(self, token: str) -> int:
        """解码访问令牌"""
        return self._decode_token(token, TokenTypeEnum.ACCESS_TOKEN)

    def decode_refresh_token(self, token: str) -> int:
        """解码刷新令牌"""
        return self._decode_token(token, TokenTypeEnum.REFRESH_TOKEN)

    def auth_access_dependency(self, auth: Optional[HTTPAuthorizationCredentials] = Security(security)) -> int:
        """
        FastAPI依赖注入：验证访问令牌
        """
        if not auth:
            logger.warning("Missing authorization header")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="缺少认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(self, auth: Optional[HTTPAuthorizationCredentials] = Security(security)) -> int:
        """
        FastAPI依赖注入：验证刷新令牌
        """
        if not auth:
            logger.warning("Missing authorization header for refresh")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="缺少认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return self.decode_refresh_token(auth.credentials)