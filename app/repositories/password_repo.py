import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def verify_old_password(db: AsyncSession, user_id: str, old_password: str):
    stmt = select(User).where(User.id == user_id)
    user = await db.scalar(stmt)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 改用 _password 字段，直接使用bcrypt验证
    try:
        is_valid = bcrypt.checkpw(old_password.encode('utf-8'), user._password.encode('utf-8'))
    except Exception:
        # 极端情况：若密码是明文（理论上不会发生）
        is_valid = (old_password == user._password)
        if is_valid:
            # 将明文密码转换为bcrypt哈希
            salt = bcrypt.gensalt()
            user._password = bcrypt.hashpw(old_password.encode('utf-8'), salt).decode('utf-8')
            await db.commit()
            await db.refresh(user)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="旧密码错误"
        )
    return user


async def change_password(
        db: AsyncSession,
        user_id: str,
        old_password: str,
        new_password: str
):
    user = await verify_old_password(db, user_id, old_password)

    # 检查新密码是否与旧密码相同（直接使用bcrypt验证）
    if bcrypt.checkpw(new_password.encode('utf-8'), user._password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )

    # 更新为新的bcrypt哈希密码
    salt = bcrypt.gensalt()
    user._password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
    await db.commit()
    await db.refresh(user)
    return {"message": "密码修改成功"}