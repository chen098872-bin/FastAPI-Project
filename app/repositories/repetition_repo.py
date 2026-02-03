from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func, desc

from app.models import AsyncSession
from app.models.usage import NameUsage


class RepetitionRepo:
    """名字重复率计算仓库（封装数据库操作）"""
    def __init__(self, session: AsyncSession):
        self.session = session  # 注入异步会话

    async def calculate(
        self,
        name: str,
        gender: str,
        region: Optional[str] = None
    ) -> dict:
        """
        计算指定名字的重复率
        :param name: 名字（如“张伟”）
        :param gender: 性别（“男”/“女”）
        :param region: 地区（可选，如“北京”）
        :return: 包含重复率的字典（符合RepetitionOut模型）
        """
        # 1. 构建基础查询条件（名字+性别，可选地区）
        base_filter = (NameUsage.name == name) & (NameUsage.gender == gender)
        if region:
            base_filter &= (NameUsage.region == region)

        # 2. 统计重复数（同名同条件的记录数）
        repeat_count = await self.session.scalar(
            select(func.count()).where(base_filter)
        ) or 0  # 处理无记录时的None

        # 3. 统计总样本量（同性别/同地区的总记录数）
        total_filter = (NameUsage.gender == gender)
        if region:
            total_filter &= (NameUsage.region == region)
        total_population = await self.session.scalar(
            select(func.count()).where(total_filter)
        ) or 0  # 处理无记录时的None

        # 4. 计算重复率（避免除以0）
        repetition_rate = round(
            repeat_count / total_population, 6
        ) if total_population > 0 else 0.0

        # 5. 获取数据最后更新时间（最新记录的时间）
        latest_time = await self.session.scalar(
            select(func.max(NameUsage.recorded_at)).where(base_filter)
        )
        data_updated_at = latest_time or datetime.now()  # 无记录时用当前时间

        return {
            "name": name,
            "gender": gender,
            "region": region,
            "repeat_count": repeat_count,
            "total_population": total_population,
            "repetition_rate": repetition_rate,
            "data_updated_at": data_updated_at
        }

    async def get_top_names(
            self,
            gender: Optional[str] = None,  # 可选按性别筛选
            limit: int = 10  # 默认返回前10
    ) -> List[dict]:
        """
        获取使用次数最多的前N个名字
        :param gender: 可选性别筛选（“男”/“女”，None表示所有性别）
        :param limit: 返回数量（默认10）
        :return: 包含名字、使用次数、性别的列表
        """
        # 1. 构建查询条件（可选按性别筛选）
        base_filter = None
        if gender:
            base_filter = (NameUsage.gender == gender)

        # 2. 构建分组统计查询：按名字+性别分组，统计次数，降序排序
        stmt = (
            select(
                NameUsage.name,  # 名字
                func.count().label("count"),  # 统计次数，别名count
                NameUsage.gender  # 性别
            )
            .where(base_filter)  # 应用筛选条件（若有）
            .group_by(NameUsage.name, NameUsage.gender)  # 按名字+性别分组
            .order_by(desc("count"))  # 按次数降序排序
            .limit(limit)  # 限制返回数量
        )

        # 3. 执行查询，获取结果
        result = await self.session.execute(stmt)
        rows = result.all()  # 返回元组列表，如 [(张伟, 2900, 男), (李娜, 1200, 女), ...]

        # 4. 转换结果格式，添加排名
        top_names = []
        for idx, row in enumerate(rows, 1):  # idx从1开始（排名1-10）
            top_names.append({
                "name": row.name,
                "count": row.count,
                "gender": row.gender,
                "rank": idx
            })

        return top_names