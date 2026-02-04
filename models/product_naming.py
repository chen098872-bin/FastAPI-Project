"""
产品起名相关数据库模型
"""

from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON, Text
from datetime import datetime


class ProductNameHistory(Base):
    """产品起名历史记录"""
    __tablename__ = "product_name_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), comment="关联用户ID")

    # 产品信息
    product_type: Mapped[str] = mapped_column(String(100), comment="产品类型")
    product_function: Mapped[str] = mapped_column(Text, comment="产品功能")
    target_audience: Mapped[str] = mapped_column(String(200), nullable=True, comment="目标用户群体")
    market_positioning: Mapped[str] = mapped_column(String(200), nullable=True, comment="市场定位")

    # 生成参数
    length: Mapped[str] = mapped_column(String(20), comment="字数要求")
    style: Mapped[str] = mapped_column(String(50), nullable=True, comment="风格偏好")
    exclude: Mapped[list] = mapped_column(JSON, default=list, comment="排除词汇")

    # 生成结果
    generated_names: Mapped[dict] = mapped_column(JSON, comment="生成的产品名称结果")
    model_used: Mapped[str] = mapped_column(String(50), comment="使用的模型")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="生成时间")

    # 关联收藏
    favorites: Mapped[list["ProductNameFavorite"]] = relationship(
        "ProductNameFavorite",
        back_populates="product_history",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_type": self.product_type,
            "product_function": self.product_function,
            "target_audience": self.target_audience,
            "market_positioning": self.market_positioning,
            "length": self.length,
            "style": self.style,
            "exclude": self.exclude,
            "generated_names": self.generated_names,
            "model_used": self.model_used,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class ProductNameFavorite(Base):
    """产品起名收藏"""
    __tablename__ = "product_name_favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), comment="收藏的用户ID")
    history_id: Mapped[int] = mapped_column(ForeignKey("product_name_history.id", ondelete="CASCADE"), comment="关联的产品起名历史记录ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间")

    # 定义关联关系
    product_history: Mapped["ProductNameHistory"] = relationship(
        "ProductNameHistory",
        back_populates="favorites"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "history_id": self.history_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "history_info": self.product_history.to_dict() if hasattr(self, "product_history") else None
        }
