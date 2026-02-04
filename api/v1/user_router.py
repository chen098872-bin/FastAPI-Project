# user_router.py
import os
import uuid
import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile

from app.core.deps import get_session
from app.models import AsyncSession
from app.repositories.password_repo import change_password
from app.repositories.user_repo import UserRepository
from app.schemas import ResponseOut
from app.core.auth import AuthHandler
from app.core.config import AVATAR_DIR, AVATAR_BASE_URL
from app.schemas.password import PasswordChangeRequest
from app.schemas.user_schemas import UserProfileResponse, UserProfileUpdate, AvatarUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])
auth_handler = AuthHandler()

# ========== 1. 获取用户资料 ==========
@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

# ========== 2. 更新用户资料 ==========
@router.put("/profile", response_model=ResponseOut)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    # 将Pydantic模型转为字典（过滤掉None值）
    update_data = profile_data.model_dump(exclude_none=True)
    await user_repo.update_user(user, update_data)
    return ResponseOut(result="success", message="资料更新成功")

# ========== 3. 上传头像 ==========
@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    # 校验文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持上传图片文件（jpg/png/jpeg等）"
        )
    # 生成唯一文件名（避免重复）
    file_ext = file.filename.split(".")[-1]
    filename = f"avatar_{current_user_id}_{uuid.uuid4()}.{file_ext}"
    file_path = AVATAR_DIR / filename
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(await file.read())
    # 更新用户头像URL
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(current_user_id)
    avatar_url = f"{AVATAR_BASE_URL}{filename}"
    await user_repo.update_user(user, {"avatar": avatar_url})
    return AvatarUploadResponse(avatar_url=avatar_url)

# ========== 4. 用户注销（物理删除） ==========
@router.post("/deleteuser", response_model=ResponseOut)
async def user_logout(
    current_user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session)
    logout_success = await user_repo.logout_user(user_id=current_user_id)
    if not logout_success:
        logger.warning(f"用户ID {current_user_id} 注销失败：用户不存在或删除异常")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注销失败：用户不存在或已注销"
        )
    return ResponseOut(result="success", message="用户已永久注销")

# ========== 5. 修改密码 ==========
@router.put("/change-password")
async def update_password(
    pwd_in: PasswordChangeRequest,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(auth_handler.auth_access_dependency)
):
    result = await change_password(
        db=db,
        user_id=current_user_id,
        old_password=pwd_in.old_password,
        new_password=pwd_in.new_password
    )
    return result