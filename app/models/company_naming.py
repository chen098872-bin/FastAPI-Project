"""
企业起名相关数据库模型
"""

from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON, Text
from datetime import datetime


class CompanyNameHistory(Base):
    """企业起名历史记录"""
    __tablename__ = "company_name_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), comment="关联用户ID")

    # 企业信息
    industry: Mapped[str] = mapped_column(String(100), comment="所属行业")
    company_type: Mapped[str] = mapped_column(String(50), comment="企业类型")
    business_scope: Mapped[str] = mapped_column(Text, comment="经营范围")
    positioning: Mapped[str] = mapped_column(String(200), nullable=True, comment="市场定位")

    # 生成参数
    length: Mapped[str] = mapped_column(String(20), comment="字数要求")
    style: Mapped[str] = mapped_column(String(50), nullable=True, comment="风格偏好")
    exclude: Mapped[list] = mapped_column(JSON, default=list, comment="排除词汇")

    # 生成结果
    generated_names: Mapped[dict] = mapped_column(JSON, comment="生成的企业名称结果")
    model_used: Mapped[str] = mapped_column(String(50), comment="使用的模型")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="生成时间")

    # 关联收藏
    favorites: Mapped[list["CompanyNameFavorite"]] = relationship(
        "CompanyNameFavorite",
        back_populates="company_history",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "industry": self.industry,
            "company_type": self.company_type,
            "business_scope": self.business_scope,
            "positioning": self.positioning,
            "length": self.length,
            "style": self.style,
            "exclude": self.exclude,
            "generated_names": self.generated_names,
            "model_used": self.model_used,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class CompanyNameFavorite(Base):
    """企业起名收藏"""
    __tablename__ = "company_name_favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), comment="收藏的用户ID")
    history_id: Mapped[int] = mapped_column(ForeignKey("company_name_history.id", ondelete="CASCADE"), comment="关联的企业起名历史记录ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间")

    # 联合唯一约束
    __table_args__ = (
        {"schema": None},  # 可选：指定schema
    )

    # 定义关联关系
    company_history: Mapped["CompanyNameHistory"] = relationship(
        "CompanyNameHistory",
        back_populates="favorites"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "history_id": self.history_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "history_info": self.company_history.to_dict() if hasattr(self, "company_history") else None
        }
