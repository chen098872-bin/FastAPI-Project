# user_schemas.py
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, model_validator

# 原有模型保留
UsernameStr = Annotated[str, Field(min_length=3, max_length=20, description="用户名")]
PasswordStr = Annotated[str, Field(min_length=6, max_length=20, description="密码")]

class RegisterIn(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: PasswordStr
    confirm_password: PasswordStr
    code: Annotated[str, Field(min_length=4, max_length=4, description="邮箱验证码")]

    @model_validator(mode="after")
    def password_is_math(self):
        if self.password != self.confirm_password:
            raise ValueError("两个密码不一致！")
        return self

class UserCreateSchema(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: PasswordStr

class LoginIn(BaseModel):
    email: EmailStr
    password: PasswordStr

class UserSchema(BaseModel):
    id: Annotated[int, Field(...)]
    email: EmailStr
    username: UsernameStr

    class Config:
        from_attributes = True  # 支持从ORM模型转换

class LoginOut(BaseModel):
    user: UserSchema
    token: str

# ********** 新增：用户资料相关模型 **********
# 用户资料响应模型（返回给前端的字段）
class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    nickname: str
    gender: str
    avatar: str
    phone: str

    class Config:
        from_attributes = True  # 支持ORM模型转换

# 用户资料更新模型（前端传入的修改字段）
class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=100, description="用户昵称")
    gender: Optional[str] = Field(None, pattern="^(男|女|未知)$", description="性别（男/女/未知）")
    phone: Optional[str] = Field(None, min_length=11, max_length=11, description="11位手机号")

# 头像上传响应模型
class AvatarUploadResponse(BaseModel):
    avatar_url: str
    message: str = "头像上传成功"