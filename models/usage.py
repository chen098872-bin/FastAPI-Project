from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, Index
from datetime import datetime


class NameUsage(Base):
    __tablename__ = "name_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="名字（如“张伟”）")
    gender: Mapped[str] = mapped_column(String(10), nullable=False, comment="性别（男/女）")
    region: Mapped[str] = mapped_column(String(50), nullable=True, comment="地区（如“北京”，可选）")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="记录采集时间")

    # 关键索引：加速“名字+性别”查询（必加，否则大数据量下统计极慢）
    __table_args__ = (Index("idx_name_gender", "name", "gender"),)