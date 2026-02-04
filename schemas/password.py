from pydantic import BaseModel, Field, validator
from typing import Optional

# 修改密码请求体
class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码（至少8位）")
    confirm_new_password: str = Field(..., description="确认新密码")

    # 验证新密码和确认密码是否一致
    @validator("confirm_new_password")
    def passwords_match(cls, v, values, **kwargs):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("新密码和确认密码不一致")
        return v

    # # 验证新密码复杂度（可选，如包含字母+数字）
    # @validator("new_password")
    # def password_complexity(cls, v):
    #     if not any(char.isalpha() for char in v) or not any(char.isdigit() for char in v):
    #         raise ValueError("新密码需包含至少一个字母和一个数字")
    #     return v