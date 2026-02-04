from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List

class NameHistoryOut(BaseModel):
    id: int
    input_params: Dict  # 输入参数（姓氏、性别等）
    generated_names: Dict  # 生成的名字结果
    model_used: str
    created_at: datetime  # 生成时间

    class Config:
        from_attributes = True  # 支持从ORM模型转换

class BatchDeleteHistoryRequest(BaseModel):
    """批量删除历史记录的请求体模型"""
    history_ids: List[int] = Field(..., min_items=1, description="待删除的历史记录ID列表，至少1个")