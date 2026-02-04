"""
AI 模型相关的 Pydantic Schema 定义
包含姓名生成、测评等结构化数据模型
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Annotated, List, Optional
from enum import Enum


class GenderEnum(str, Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"
    UNKNOWN = "未知"


class NameLengthEnum(str, Enum):
    """名字长度枚举"""
    TWO_CHARS = "两字"
    THREE_CHARS = "三字"
    FOUR_CHARS = "四字"


class NameSchema(BaseModel):
    """基础姓名 Schema"""
    surname: Annotated[str, Field(..., min_length=1, max_length=5, description="姓氏")]
    given_name: Annotated[str, Field(..., min_length=1, max_length=10, description="名字（不含姓氏）")]
    reference: Annotated[str, Field(default="", description="出处或来源")]
    meaning: Annotated[str, Field(default="", description="寓意和含义")]

    @field_validator('surname', 'given_name')
    @classmethod
    def validate_chinese_chars(cls, v: str) -> str:
        """验证是否为中文字符"""
        if not all('\u4e00' <= char <= '\u9fff' for char in v):
            raise ValueError('必须是中文字符')
        return v

    @property
    def full_name(self) -> str:
        """完整姓名属性"""
        return f"{self.surname}{self.given_name}"

    @property
    def total_length(self) -> int:
        """总字数"""
        return len(self.surname) + len(self.given_name)


class NameResultSchema(BaseModel):
    """姓名生成结果"""
    names: Annotated[List[NameSchema], Field(min_length=1, max_length=10)]
    generated_at: Optional[str] = None
    model_used: Optional[str] = None

    @model_validator(mode='after')
    def validate_names_not_empty(self):
        """确保至少有一个有效名字"""
        if not self.names:
            raise ValueError("至少需要生成一个名字")
        return self


class CompanyNameSchema(BaseModel):
    """企业名称 Schema"""
    name: Annotated[str, Field(..., min_length=2, max_length=50, description="企业名称")]
    meaning: Annotated[str, Field(..., min_length=10, max_length=500, description="名称寓意和含义")]
    advantages: Annotated[List[str], Field(..., min_length=1, max_length=5, description="名称优势列表")]
    suitable_industry: Annotated[str, Field(..., min_length=2, max_length=100, description="适合的行业或领域")]
    brand_value: Optional[Annotated[str, Field(default="", max_length=200)]] = None

    @field_validator('name')
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        """验证企业名称不包含禁用词汇"""
        forbidden_words = ['测试', '临时', '垃圾', '非法']
        for word in forbidden_words:
            if word in v:
                raise ValueError(f'企业名称不能包含禁用词汇: {word}')
        return v


class CompanyNameResultSchema(BaseModel):
    """企业起名结果"""
    names: Annotated[List[CompanyNameSchema], Field(min_length=1, max_length=5)]
    industry: Optional[str] = None
    company_type: Optional[str] = None


class ProductNameSchema(BaseModel):
    """产品名称 Schema"""
    name: Annotated[str, Field(..., min_length=1, max_length=30, description="产品名称")]
    meaning: Annotated[str, Field(..., min_length=10, max_length=300, description="名称寓意和含义")]
    features: Annotated[List[str], Field(..., min_length=1, max_length=5, description="名称特点列表")]
    target_audience: Annotated[str, Field(..., min_length=2, max_length=100, description="目标用户群体")]
    market_positioning: Annotated[str, Field(..., min_length=2, max_length=100, description="市场定位")]
    slogan: Optional[Annotated[str, Field(default="", max_length=100)]] = None


class ProductNameResultSchema(BaseModel):
    """产品起名结果"""
    names: Annotated[List[ProductNameSchema], Field(min_length=1, max_length=5)]
    product_type: Optional[str] = None
    target_market: Optional[str] = None


# ===== 姓名测评相关 Schema =====

class AuspiciousnessEnum(str, Enum):
    """吉凶评级枚举"""
    GREAT_AUSPICIOUS = "大吉"
    AUSPICIOUS = "吉"
    NEUTRAL = "中"
    INAUSPICIOUS = "凶"
    GREAT_INAUSPICIOUS = "大凶"


class FiveElementsEnum(str, Enum):
    """五行枚举"""
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"


class CulturalConnotation(BaseModel):
    """文化内涵分析"""
    quote: Annotated[str, Field(..., min_length=2, max_length=200, description="相关诗句或名言")]
    quote_source: Annotated[str, Field(..., min_length=2, max_length=100, description="诗句出处")]
    meaning_explanation: Annotated[str, Field(..., min_length=10, max_length=500, description="字义解释和文化内涵")]


class FiveGridAnalysis(BaseModel):
    """五格分析"""
    number: Annotated[int, Field(ge=1, le=81, description="格的数值（1-81）")]
    auspiciousness: Annotated[AuspiciousnessEnum, Field(..., description="吉凶评级")]
    element: Annotated[FiveElementsEnum, Field(..., description="五行属性")]


class ThreeTalentsFiveGrids(BaseModel):
    """三才五格分析"""
    tiange: Annotated[FiveGridAnalysis, Field(..., description="天格")]
    renge: Annotated[FiveGridAnalysis, Field(..., description="人格")]
    dige: Annotated[FiveGridAnalysis, Field(..., description="地格")]
    waige: Annotated[FiveGridAnalysis, Field(..., description="外格")]
    zongge: Annotated[FiveGridAnalysis, Field(..., description="总格")]
    three_talents_config: Annotated[str, Field(..., min_length=3, max_length=10, description="三才配置")]
    three_talents_description: Annotated[str, Field(..., min_length=10, max_length=300, description="三才配置的描述和评价")]


class FiveElementsDistribution(BaseModel):
    """五行分布分析"""
    metal: Annotated[int, Field(ge=0, le=10, description="金的数量")]
    wood: Annotated[int, Field(ge=0, le=10, description="木的数量")]
    water: Annotated[int, Field(ge=0, le=10, description="水的数量")]
    fire: Annotated[int, Field(ge=0, le=10, description="火的数量")]
    earth: Annotated[int, Field(ge=0, le=10, description="土的数量")]
    auspicious_element: Annotated[FiveElementsEnum, Field(..., description="喜用神")]
    element_advice: Annotated[str, Field(..., min_length=10, max_length=300, description="五行建议说明")]

    @field_validator('auspicious_element')
    @classmethod
    def validate_auspicious_element(cls, v):
        """验证喜用神是有效的五行元素"""
        if v not in [e.value for e in FiveElementsEnum]:
            raise ValueError('喜用神必须是有效的五行元素')
        return v


class FortuneAnalysis(BaseModel):
    """运势详解"""
    personality: Annotated[str, Field(..., min_length=20, max_length=500, description="性格分析")]
    career: Annotated[str, Field(..., min_length=20, max_length=500, description="事业分析")]
    health: Annotated[str, Field(..., min_length=20, max_length=300, description="健康分析")]


class NameEvaluationSchema(BaseModel):
    """姓名测评完整结果"""

    # 基本信息
    full_name: Annotated[str, Field(..., min_length=2, max_length=15, description="完整姓名")]
    summary: Annotated[str, Field(..., min_length=10, max_length=200, description="整体印象总结")]

    # 综合评分
    overall_score: Annotated[int, Field(ge=0, le=100, description="综合评分（0-100）")]
    auspicious_rating: Annotated[AuspiciousnessEnum, Field(..., description="吉凶评级")]
    score_description: Annotated[str, Field(..., min_length=10, max_length=300, description="评分详细描述")]

    # 基础评分维度
    pronunciation_score: Annotated[int, Field(ge=0, le=100, description="音律评分")]
    meaning_score: Annotated[int, Field(ge=0, le=100, description="含义评分")]
    uniqueness_score: Annotated[int, Field(ge=0, le=100, description="独特性评分")]

    # 专业分析
    cultural_connotation: Annotated[CulturalConnotation, Field(..., description="文化内涵分析")]
    three_talents_five_grids: Annotated[ThreeTalentsFiveGrids, Field(..., description="三才五格分析")]
    five_elements: Annotated[FiveElementsDistribution, Field(..., description="五行分布分析")]
    fortune_analysis: Annotated[FortuneAnalysis, Field(..., description="运势详解")]

    # 优缺点和建议
    advantages: Annotated[List[str], Field(min_length=2, max_length=10, description="优点列表")]
    disadvantages: Annotated[List[str], Field(min_length=1, max_length=5, description="缺点列表")]
    advice: Annotated[str, Field(..., min_length=20, max_length=500, description="综合建议")]

    @field_validator('advantages', 'disadvantages')
    @classmethod
    def validate_list_items(cls, v: List[str]) -> List[str]:
        """验证列表项不为空"""
        for item in v:
            if not item.strip():
                raise ValueError('列表项不能为空')
            if len(item) < 5:
                raise ValueError('列表项至少5个字符')
        return v

    @model_validator(mode='after')
    def validate_scores_consistency(self):
        """验证评分与评级的一致性"""
        score = self.overall_score
        rating = self.auspicious_rating

        # 高分应该对应好的评级，低分对应差的评级
        if score >= 80 and rating in [AuspiciousnessEnum.INAUSPICIOUS, AuspiciousnessEnum.GREAT_INAUSPICIOUS]:
            raise ValueError('高分不应对应差的吉凶评级')
        if score <= 30 and rating in [AuspiciousnessEnum.GREAT_AUSPICIOUS, AuspiciousnessEnum.AUSPICIOUS]:
            raise ValueError('低分不应对应好的吉凶评级')

        return self