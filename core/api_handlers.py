"""
通用API处理器
用于减少重复的CRUD操作代码
"""

import logging
from typing import List, Dict, Any, Type, Generic, TypeVar, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthHandler
from app.core.deps import get_session
from app.schemas.responses import APIResponse, ResponseCode, success_response, error_response

logger = logging.getLogger(__name__)

T = TypeVar('T')


class GenericAPIHandler:
    """通用API处理器"""

    def __init__(self):
        self.auth_handler = AuthHandler()

    async def handle_history_list(
        self,
        repository_class: Type,
        response_model: Type[T],
        user_id: int,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        operation_name: str = "获取历史记录"
    ) -> List[T]:
        """
        通用历史记录列表处理

        Args:
            repository_class: Repository类
            response_model: 响应模型类
            user_id: 用户ID
            session: 数据库会话
            page: 页码
            page_size: 每页数量
            operation_name: 操作名称（用于日志）

        Returns:
            历史记录列表
        """
        try:
            repo = repository_class(session)
            histories = await repo.get_history_by_user(user_id, page, page_size)

            return [response_model(**history.to_dict()) for history in histories]

        except Exception as e:
            logger.error(f"Failed to {operation_name.lower()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}失败"
            )

    async def handle_history_delete(
        self,
        repository_class: Type,
        history_id: int,
        user_id: int,
        session: AsyncSession,
        operation_name: str = "删除历史记录"
    ) -> None:
        """
        通用历史记录删除处理

        Args:
            repository_class: Repository类
            history_id: 历史记录ID
            user_id: 用户ID
            session: 数据库会话
            operation_name: 操作名称（用于日志）
        """
        try:
            repo = repository_class(session)
            success = await repo.delete_history(history_id, user_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="历史记录不存在或无权限删除"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to {operation_name.lower()} {history_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}失败"
            )

    async def handle_favorite_add(
        self,
        repository_class: Type,
        history_id: int,
        user_id: int,
        session: AsyncSession,
        operation_name: str = "添加收藏"
    ) -> Dict[str, str]:
        """
        通用添加收藏处理

        Args:
            repository_class: Repository类
            history_id: 历史记录ID
            user_id: 用户ID
            session: 数据库会话
            operation_name: 操作名称（用于日志）

        Returns:
            响应消息
        """
        try:
            repo = repository_class(session)
            favorite = await repo.add_to_favorites(user_id, history_id)

            return {"message": f"{operation_name}成功", "favorite_id": favorite.id}

        except ValueError as e:
            logger.warning(f"Validation error during {operation_name.lower()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{operation_name}失败：{str(e)}"
            )
        except Exception as e:
            logger.error(f"Failed to {operation_name.lower()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}失败，请稍后重试"
            )

    async def handle_favorite_remove(
        self,
        repository_class: Type,
        history_id: int,
        user_id: int,
        session: AsyncSession,
        operation_name: str = "移除收藏"
    ) -> Dict[str, str]:
        """
        通用移除收藏处理

        Args:
            repository_class: Repository类
            history_id: 历史记录ID
            user_id: 用户ID
            session: 数据库会话
            operation_name: 操作名称（用于日志）

        Returns:
            响应消息
        """
        try:
            repo = repository_class(session)
            success = await repo.remove_from_favorites(user_id, history_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="收藏记录不存在"
                )

            return {"message": f"{operation_name}成功"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to {operation_name.lower()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}失败"
            )

    async def handle_favorites_list(
        self,
        repository_class: Type,
        user_id: int,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        operation_name: str = "获取收藏列表"
    ) -> List[Dict]:
        """
        通用收藏列表处理

        Args:
            repository_class: Repository类
            user_id: 用户ID
            session: 数据库会话
            page: 页码
            page_size: 每页数量
            operation_name: 操作名称（用于日志）

        Returns:
            收藏列表
        """
        try:
            repo = repository_class(session)
            favorites = await repo.get_favorites_by_user(user_id, page, page_size)

            return [favorite.to_dict() for favorite in favorites]

        except Exception as e:
            logger.error(f"Failed to {operation_name.lower()}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}失败"
            )


# 全局API处理器实例
api_handler = GenericAPIHandler()
