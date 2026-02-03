from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON, UniqueConstraint
from datetime import datetime

# NameHistory模型
class NameHistory(Base):
    __tablename__ = "name_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), comment="关联用户ID")
    input_params: Mapped[dict] = mapped_column(JSON, comment="生成名字的输入参数（姓氏、性别等）")
    generated_names: Mapped[dict] = mapped_column(JSON, comment="生成的名字结果")
    model_used: Mapped[str] = mapped_column(String(50), comment="使用的模型（deepseek/alibaba）")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="生成时间")

    # 关键修改：用back_populates替代backref，指定反向关联的属性名
    favorites: Mapped[list["NameFavorite"]] = relationship(
        "NameFavorite",
        back_populates="name_history",  # 对应NameFavorite中的name_history属性
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "input_params": self.input_params,
            "generated_names": self.generated_names,
            "model_used": self.model_used,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

# NameFavorite模型
class NameFavorite(Base):
    __tablename__ = "name_favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), comment="收藏的用户ID")
    history_id: Mapped[int] = mapped_column(ForeignKey("name_history.id", ondelete="CASCADE"), comment="关联的姓名历史记录ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间")

    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint("user_id", "history_id", name="uq_user_history"),
    )

    # 关键修改：定义关联关系，用back_populates对应NameHistory中的favorites属性
    name_history: Mapped["NameHistory"] = relationship(
        "NameHistory",
        back_populates="favorites"  # 对应NameHistory中的favorites属性
    )

    def to_dict(self):
        return {
            "id": self.id,
            "history_id": self.history_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "history_info": self.name_history.to_dict() if hasattr(self, "name_history") else None
        }