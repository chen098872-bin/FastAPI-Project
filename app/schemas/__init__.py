# schemas/__init__.py
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, Any

class ResponseOut(BaseModel):
    result: Annotated[Literal["success", "failure"], Field("success", description="操作结果")]
    message: Optional[str] = Field(None, description="提示信息")
    data: Optional[Any] = Field(None, description="返回数据")