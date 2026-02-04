from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
from .agent import (
    NameSchema,
    NameEvaluationSchema,
    CompanyNameSchema,
    CompanyNameResultSchema,
    ProductNameSchema,
    ProductNameResultSchema,
)

class NameIn(BaseModel):
    surname: Annotated[str, Field(..., description="姓氏")]
    gender: Annotated[Literal["不限", "男", "女"], Field(..., description="性别")]
    length: Annotated[Literal["不限", "单字", "两字"], Field(..., description="字数")]
    other: Annotated[str|None, Field("", description="其他要求")]
    exclude: Annotated[List[str], Field([], description="排除的名字")]

class NameOut(BaseModel):
    names: List[NameSchema]


class NameEvaluateIn(BaseModel):
    full_name: Annotated[str, Field(..., description="需要测评的完整姓名，如：张三")]
    gender: Annotated[Literal["不限", "男", "女", "未知"], Field("不限", description="性别，可选")] = "不限"
    birthdate: Annotated[str | None, Field(None, description="出生日期，选填，格式如 2000-01-01")]


class NameEvaluateOut(NameEvaluationSchema):
    """直接复用 Agent 输出的测评结构"""
    pass




# 收藏/取消收藏的请求模型（传入历史记录ID）
class FavoriteRequest(BaseModel):
    history_id: int = Field(..., gt=0, description="姓名历史记录ID（必须大于0）")

# 收藏项的响应模型
class FavoriteItemResponse(BaseModel):
    id: int
    history_id: int
    created_at: str
    history_info: dict

# 收藏列表的响应模型
class FavoriteListResponse(BaseModel):
    total: int
    items: List[FavoriteItemResponse]


# ========== 企业起名相关 ==========
class CompanyNameIn(BaseModel):
    """企业起名请求"""
    industry: Annotated[str, Field(..., description="所属行业，如：科技、餐饮、教育、金融等")]
    company_type: Annotated[str, Field(..., description="企业类型，如：有限公司、股份公司、集团等")]
    business_scope: Annotated[str, Field(..., description="经营范围或业务描述")]
    positioning: Annotated[str | None, Field(None, description="市场定位，如：高端、大众、创新等")]
    length: Annotated[Literal["2字", "3字", "4字", "不限"], Field("不限", description="名称字数要求")]
    style: Annotated[str | None, Field(None, description="风格偏好，如：传统、现代、国际化、本土化等")]
    exclude: Annotated[List[str], Field([], description="排除的字或词")]


class CompanyNameOut(BaseModel):
    """企业起名响应"""
    names: List[CompanyNameSchema]


# ========== 产品起名相关 ==========
class ProductNameIn(BaseModel):
    """产品起名请求"""
    product_type: Annotated[str, Field(..., description="产品类型，如：APP、软件、食品、服装等")]
    product_function: Annotated[str, Field(..., description="产品功能或特点描述")]
    target_audience: Annotated[str | None, Field(None, description="目标用户群体，如：年轻人、商务人士、学生等")]
    market_positioning: Annotated[str | None, Field(None, description="市场定位，如：高端、性价比、创新等")]
    length: Annotated[Literal["2字", "3字", "4字", "不限"], Field("不限", description="名称字数要求")]
    style: Annotated[str | None, Field(None, description="风格偏好，如：简洁、科技感、文艺、时尚等")]
    exclude: Annotated[List[str], Field([], description="排除的字或词")]


class ProductNameOut(BaseModel):
    """产品起名响应"""
    names: List[ProductNameSchema]