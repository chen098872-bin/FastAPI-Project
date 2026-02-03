from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUserDep, SessionDep
from app.schemas.name import FavoriteRequest
from app.repositories.favorite_repo import (
    add_favorite,
    remove_favorite,
    get_user_favorites,
)

router = APIRouter(prefix="/favorite", tags=["收藏管理"])

# --------------------------
# 添加收藏接口
# --------------------------
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_name_favorite(
    req: FavoriteRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    favorite = await add_favorite(db, current_user.id, req.history_id)
    return {"message": "收藏成功", "favorite_id": favorite.id}

# --------------------------
# 取消收藏接口
# --------------------------
@router.post("/remove", status_code=status.HTTP_200_OK)
async def remove_name_favorite(
    req: FavoriteRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    await remove_favorite(db, current_user.id, req.history_id)
    return {"message": "取消收藏成功"}

# --------------------------
# 获取收藏列表接口
# --------------------------
@router.get("/list", status_code=status.HTTP_200_OK)
async def get_favorite_list(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    return await get_user_favorites(db, current_user.id)