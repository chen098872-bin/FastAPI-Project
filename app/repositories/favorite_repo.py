from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.history_test import NameFavorite, NameHistory
from app.models.company_naming import CompanyNameHistory, CompanyNameFavorite
from app.models.product_naming import ProductNameHistory, ProductNameFavorite
from app.models.user import User


# 识别历史记录类型和对应的收藏表
async def _identify_history_and_favorite_type(db: AsyncSession, user_id: int, history_id: int):
    """识别历史记录类型，返回 (history, favorite_class, history_type)"""
    # 1. 检查孩子起名历史记录
    name_history = await db.scalar(
        select(NameHistory).where(NameHistory.id == history_id, NameHistory.user_id == user_id)
    )
    if name_history:
        return name_history, NameFavorite, "name"

    # 2. 检查企业起名历史记录
    company_history = await db.scalar(
        select(CompanyNameHistory).where(CompanyNameHistory.id == history_id, CompanyNameHistory.user_id == user_id)
    )
    if company_history:
        return company_history, CompanyNameFavorite, "company"

    # 3. 检查产品起名历史记录
    product_history = await db.scalar(
        select(ProductNameHistory).where(ProductNameHistory.id == history_id, ProductNameHistory.user_id == user_id)
    )
    if product_history:
        return product_history, ProductNameFavorite, "product"

    # 4. 没有找到任何类型的历史记录
    return None, None, None


# 收藏某次生成记录
async def add_favorite(db: AsyncSession, user_id: int, history_id: int):
    # 1. 检查用户是否存在
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 识别历史记录类型和对应的收藏表
    history, favorite_class, history_type = await _identify_history_and_favorite_type(db, user_id, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在或无权限")

    # 3. 检查是否已收藏（需要检查对应的收藏表）
    existing_favorite = await db.scalar(
        select(favorite_class).where(
            favorite_class.user_id == user_id,
            favorite_class.history_id == history_id
        )
    )
    if existing_favorite:
        raise HTTPException(status_code=400, detail="该记录已收藏")

    # 4. 创建收藏记录
    new_favorite = favorite_class(user_id=user_id, history_id=history_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return new_favorite


# 取消收藏某次生成记录
async def remove_favorite(db: AsyncSession, user_id: int, history_id: int):
    # 1. 识别历史记录类型和对应的收藏表
    history, favorite_class, history_type = await _identify_history_and_favorite_type(db, user_id, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在或无权限")

    # 2. 检查收藏记录是否存在
    favorite = await db.scalar(
        select(favorite_class).where(
            favorite_class.user_id == user_id,
            favorite_class.history_id == history_id
        )
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="未收藏该记录")

    # 3. 删除收藏记录
    await db.execute(
        delete(favorite_class).where(
            favorite_class.user_id == user_id,
            favorite_class.history_id == history_id
        )
    )
    await db.commit()

    return {"message": "取消收藏成功"}


# 获取用户的收藏列表（支持所有类型）
async def get_user_favorites(db: AsyncSession, user_id: int):
    all_favorites = []

    # 1. 获取孩子起名收藏
    name_result = await db.execute(
        select(NameFavorite)
        .where(NameFavorite.user_id == user_id)
        .options(joinedload(NameFavorite.name_history))
        .order_by(NameFavorite.created_at.desc())
    )
    name_favorites = name_result.scalars().all()
    for favorite in name_favorites:
        favorite_dict = favorite.to_dict()
        # 添加类型标识
        favorite_dict["type"] = "name"
        all_favorites.append(favorite_dict)

    # 2. 获取企业起名收藏
    company_result = await db.execute(
        select(CompanyNameFavorite)
        .where(CompanyNameFavorite.user_id == user_id)
        .options(joinedload(CompanyNameFavorite.company_history))
        .order_by(CompanyNameFavorite.created_at.desc())
    )
    company_favorites = company_result.scalars().all()
    for favorite in company_favorites:
        favorite_dict = favorite.to_dict()
        # 添加类型标识
        favorite_dict["type"] = "company"
        all_favorites.append(favorite_dict)

    # 3. 获取产品起名收藏
    product_result = await db.execute(
        select(ProductNameFavorite)
        .where(ProductNameFavorite.user_id == user_id)
        .options(joinedload(ProductNameFavorite.product_history))
        .order_by(ProductNameFavorite.created_at.desc())
    )
    product_favorites = product_result.scalars().all()
    for favorite in product_favorites:
        favorite_dict = favorite.to_dict()
        # 添加类型标识
        favorite_dict["type"] = "product"
        all_favorites.append(favorite_dict)

    # 4. 按创建时间倒序排序
    all_favorites.sort(key=lambda x: x["created_at"], reverse=True)

    # 构造响应数据
    return {
        "total": len(all_favorites),
        "items": all_favorites
    }