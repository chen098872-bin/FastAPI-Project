from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RepetitionOut(BaseModel):
    """名字重复率查询结果模型（API响应格式）"""
    name: str
    gender: str
    region: Optional[str]  # 允许为None（未指定地区时）
    repeat_count: int  # 同名同性别（同地区）的记录数
    total_population: int  # 同性别（同地区）的总记录数
    repetition_rate: float  # 重复率（保留6位小数）
    data_updated_at: datetime  # 数据最后更新时间

    class Config:
        """配置：支持datetime序列化及ORM模型转换"""
        from_attributes = True  # 兼容SQLAlchemy模型（可选）
        json_encoders = {
            datetime: lambda v: v.isoformat()  # 转换为ISO格式字符串（如"2023-12-09T14:52:32"）
        }

class NameTopOut(BaseModel):
    """名字使用次数Top10结果模型"""
    name: str  # 名字
    count: int  # 使用次数
    gender: Optional[str]  # 性别（若按性别筛选则返回，否则为None）
    rank: int  # 排名（1-10）