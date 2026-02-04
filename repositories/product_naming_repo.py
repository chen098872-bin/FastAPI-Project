"""
产品起名相关数据访问层
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_naming import ProductNameHistory, ProductNameFavorite
from app.schemas.name import ProductNameIn, ProductNameOut

logger = logging.getLogger(__name__)


class ProductNamingRepository:
    """产品起名数据访问类"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_history(self, user_id: int, input_params: ProductNameIn,
                           generated_names: dict, model_used: str) -> ProductNameHistory:
        """
        创建产品起名历史记录

        Args:
            user_id: 用户ID
            input_params: 输入参数
            generated_names: 生成的名称结果
            model_used: 使用的模型

        Returns:
            创建的历史记录对象
        """
        try:
            history = ProductNameHistory(
                user_id=user_id,
                product_type=input_params.product_type,
                product_function=input_params.product_function,
                target_audience=input_params.target_audience,
                market_positioning=input_params.market_positioning,
                length=input_params.length,
                style=input_params.style,
                exclude=input_params.exclude,
                generated_names=generated_names,
                model_used=model_used
            )

            self.session.add(history)
            await self.session.flush()  # 获取ID但不提交
            await self.session.refresh(history)

            logger.info(f"Created product naming history for user {user_id}")
            return history

        except Exception as e:
            logger.error(f"Failed to create product naming history: {e}")
            raise

    async def get_history_by_user(self, user_id: int, page: int = 1,
                                page_size: int = 10) -> List[ProductNameHistory]:
        """
        获取用户的产品起名历史记录

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            历史记录列表
        """
        try:
            offset = (page - 1) * page_size
            stmt = (
                select(ProductNameHistory)
                .where(ProductNameHistory.user_id == user_id)
                .order_by(desc(ProductNameHistory.created_at))
                .offset(offset)
                .limit(page_size)
            )

            result = await self.session.execute(stmt)
            histories = result.scalars().all()

            logger.debug(f"Retrieved {len(histories)} product naming histories for user {user_id}")
            return list(histories)

        except Exception as e:
            logger.error(f"Failed to get product naming history for user {user_id}: {e}")
            raise

    async def get_history_by_id(self, history_id: int, user_id: int) -> Optional[ProductNameHistory]:
        """
        根据ID获取产品起名历史记录

        Args:
            history_id: 历史记录ID
            user_id: 用户ID（用于权限验证）

        Returns:
            历史记录对象或None
        """
        try:
            stmt = (
                select(ProductNameHistory)
                .where(
                    and_(
                        ProductNameHistory.id == history_id,
                        ProductNameHistory.user_id == user_id
                    )
                )
            )

            result = await self.session.execute(stmt)
            history = result.scalar_one_or_none()

            return history

        except Exception as e:
            logger.error(f"Failed to get product naming history {history_id}: {e}")
            raise

    async def delete_history(self, history_id: int, user_id: int) -> bool:
        """
        删除产品起名历史记录

        Args:
            history_id: 历史记录ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        try:
            history = await self.get_history_by_id(history_id, user_id)
            if not history:
                return False

            await self.session.delete(history)
            logger.info(f"Deleted product naming history {history_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete product naming history {history_id}: {e}")
            raise

    async def add_to_favorites(self, user_id: int, history_id: int) -> ProductNameFavorite:
        """
        添加产品起名到收藏

        Args:
            user_id: 用户ID
            history_id: 历史记录ID

        Returns:
            收藏记录对象
        """
        try:
            # 验证历史记录存在且属于用户
            history = await self.get_history_by_id(history_id, user_id)
            if not history:
                raise ValueError("历史记录不存在或无权限访问")

            # 检查是否已收藏
            stmt = select(ProductNameFavorite).where(
                and_(
                    ProductNameFavorite.user_id == user_id,
                    ProductNameFavorite.history_id == history_id
                )
            )
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                raise ValueError("该记录已在收藏中")

            # 创建收藏记录
            favorite = ProductNameFavorite(
                user_id=user_id,
                history_id=history_id
            )

            self.session.add(favorite)
            await self.session.flush()
            await self.session.refresh(favorite)  # 刷新以获取ID

            logger.info(f"Added product naming history {history_id} to favorites for user {user_id}")
            return favorite

        except Exception as e:
            logger.error(f"Failed to add product naming to favorites: {e}")
            raise

    async def remove_from_favorites(self, user_id: int, history_id: int) -> bool:
        """
        从收藏中移除产品起名

        Args:
            user_id: 用户ID
            history_id: 历史记录ID

        Returns:
            是否移除成功
        """
        try:
            stmt = select(ProductNameFavorite).where(
                and_(
                    ProductNameFavorite.user_id == user_id,
                    ProductNameFavorite.history_id == history_id
                )
            )

            result = await self.session.execute(stmt)
            favorite = result.scalar_one_or_none()

            if not favorite:
                return False

            await self.session.delete(favorite)
            logger.info(f"Removed product naming history {history_id} from favorites for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove product naming from favorites: {e}")
            raise

    async def get_favorites_by_user(self, user_id: int, page: int = 1,
                                  page_size: int = 10) -> List[ProductNameFavorite]:
        """
        获取用户的产品起名收藏列表

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量

        Returns:
            收藏记录列表
        """
        try:
            offset = (page - 1) * page_size
            stmt = (
                select(ProductNameFavorite)
                .where(ProductNameFavorite.user_id == user_id)
                .order_by(desc(ProductNameFavorite.created_at))
                .offset(offset)
                .limit(page_size)
            )

            result = await self.session.execute(stmt)
            favorites = result.scalars().all()

            logger.debug(f"Retrieved {len(favorites)} product naming favorites for user {user_id}")
            return list(favorites)

        except Exception as e:
            logger.error(f"Failed to get product naming favorites for user {user_id}: {e}")
            raise
