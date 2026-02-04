"""
AI服务负载均衡器
提供多AI服务的负载均衡和故障转移功能
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from app.schemas.agent import NameResultSchema
from app.schemas.name import NameIn
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIServiceStatus(Enum):
    """AI服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class AIServiceInfo:
    """AI服务信息"""
    name: str
    generate_func: Callable[[NameIn], Awaitable[NameResultSchema]]
    status: AIServiceStatus = AIServiceStatus.HEALTHY
    last_used: float = 0
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0
    consecutive_failures: int = 0

    @property
    def health_score(self) -> float:
        """计算健康分数 (0-1, 越高越健康)"""
        if self.failure_count == 0:
            return 1.0

        total_requests = self.success_count + self.failure_count
        if total_requests == 0:
            return 0.5

        success_rate = self.success_count / total_requests

        # 连续失败惩罚
        failure_penalty = min(self.consecutive_failures * 0.1, 0.5)

        # 响应时间惩罚 (超过5秒的响应时间会降低分数)
        time_penalty = min(self.avg_response_time / 5.0 * 0.1, 0.3)

        return max(0, success_rate - failure_penalty - time_penalty)


class AILoadBalancer:
    """AI服务负载均衡器"""

    def __init__(self):
        self.services: Dict[str, AIServiceInfo] = {}
        self.health_check_interval = 60  # 每60秒检查一次健康状态
        self.max_consecutive_failures = 3  # 最大连续失败次数
        self.circuit_breaker_timeout = 300  # 熔断器超时时间（秒）
        self._services_registered = False  # 标记是否已注册服务

    def register_service(
        self,
        name: str,
        generate_func: Callable[[NameIn], Awaitable[NameResultSchema]],
        priority: int = 1
    ):
        """
        注册AI服务

        Args:
            name: 服务名称
            generate_func: 生成函数
            priority: 优先级（越高越优先）
        """
        self.services[name] = AIServiceInfo(
            name=name,
            generate_func=generate_func
        )
        logger.info(f"Registered AI service: {name} with priority {priority}")

    def unregister_service(self, name: str):
        """注销AI服务"""
        if name in self.services:
            del self.services[name]
            logger.info(f"Unregistered AI service: {name}")

    def _get_healthy_services(self) -> List[AIServiceInfo]:
        """获取健康的服务列表"""
        healthy_services = [
            service for service in self.services.values()
            if service.status in [AIServiceStatus.HEALTHY, AIServiceStatus.DEGRADED]
        ]
        return sorted(healthy_services, key=lambda s: s.health_score, reverse=True)

    def _select_service(self) -> Optional[AIServiceInfo]:
        """选择最优的服务（基于健康分数和负载均衡）"""
        healthy_services = self._get_healthy_services()

        if not healthy_services:
            logger.warning("No healthy AI services available")
            return None

        # 使用加权随机选择，健康分数高的服务被选中的概率更高
        total_score = sum(service.health_score for service in healthy_services)
        if total_score == 0:
            # 如果所有服务的分数都是0，随机选择一个
            return healthy_services[0]

        import random
        pick = random.uniform(0, total_score)
        current_sum = 0

        for service in healthy_services:
            current_sum += service.health_score
            if pick <= current_sum:
                return service

        # 兜底选择第一个
        return healthy_services[0]

    def _update_service_stats(
        self,
        service: AIServiceInfo,
        response_time: float,
        success: bool
    ):
        """更新服务统计信息"""
        service.last_used = time.time()

        if success:
            service.success_count += 1
            service.consecutive_failures = 0
        else:
            service.failure_count += 1
            service.consecutive_failures += 1

        # 更新平均响应时间 (使用指数移动平均)
        if service.avg_response_time == 0:
            service.avg_response_time = response_time
        else:
            alpha = 0.1  # 平滑因子
            service.avg_response_time = alpha * response_time + (1 - alpha) * service.avg_response_time

        # 更新服务状态
        if service.consecutive_failures >= self.max_consecutive_failures:
            service.status = AIServiceStatus.UNHEALTHY
            logger.warning(f"Service {service.name} marked as unhealthy due to {service.consecutive_failures} consecutive failures")
        elif service.health_score < 0.5:
            service.status = AIServiceStatus.DEGRADED
        else:
            service.status = AIServiceStatus.HEALTHY

    async def generate_names(self, name_info: NameIn) -> NameResultSchema:
        """
        生成姓名（带负载均衡和故障转移）

        Args:
            name_info: 姓名生成输入参数

        Returns:
            姓名生成结果

        Raises:
            HTTPException: 当所有服务都不可用时抛出
        """
        # 延迟注册AI服务（第一次使用时）
        if not self._services_registered:
            await self._register_services()
            self._services_registered = True
        max_attempts = len(self.services) if self.services else 1
        attempted_services = set()

        for attempt in range(max_attempts):
            service = self._select_service()

            if not service or service.name in attempted_services:
                break

            attempted_services.add(service.name)

            try:
                logger.info(f"Attempting to use AI service: {service.name} (attempt {attempt + 1})")
                start_time = time.time()

                result = await service.generate_func(name_info)

                response_time = time.time() - start_time
                self._update_service_stats(service, response_time, True)

                logger.info(f"AI service {service.name} succeeded in {response_time:.2f}s")
                return result

            except Exception as e:
                response_time = time.time() - start_time
                self._update_service_stats(service, response_time, False)

                logger.warning(f"AI service {service.name} failed (attempt {attempt + 1}): {e}")

                # 如果这是最后一个可用的服务，继续尝试其他服务
                if attempt < max_attempts - 1:
                    continue

        # 所有服务都失败了
        logger.error("All AI services failed")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI服务暂时不可用，请稍后重试。我们正在努力恢复服务。"
        )

    async def _register_services(self):
        """注册可用的AI服务"""
        try:
            # 动态导入以避免循环依赖
            if hasattr(self, '_import_services'):
                return  # 已经注册过了

            from app.core.agent_DeepSeek import generate_names as generate_names_deepseek
            from app.core.agent_Qwen import generate_names_text as generate_names_qwen

            # 注册AI服务
            if settings.DEEPSEEK_API_KEY:
                self.register_service("deepseek", generate_names_deepseek, priority=2)
                logger.info("Registered DeepSeek AI service")

            if settings.ALIBABA_API_KEY:
                self.register_service("qwen", generate_names_qwen, priority=1)
                logger.info("Registered Qwen AI service")

            # 标记为已导入
            self._import_services = True

        except Exception as e:
            logger.error(f"Failed to register AI services: {e}")

    async def get_service_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务的统计信息"""
        stats = {}
        for name, service in self.services.items():
            stats[name] = {
                "status": service.status.value,
                "health_score": round(service.health_score, 3),
                "success_count": service.success_count,
                "failure_count": service.failure_count,
                "success_rate": round(service.success_count / max(service.success_count + service.failure_count, 1), 3),
                "avg_response_time": round(service.avg_response_time, 2),
                "consecutive_failures": service.consecutive_failures,
                "last_used": service.last_used
            }
        return stats

    async def health_check(self):
        """健康检查（可作为后台任务运行）"""
        while True:
            try:
                # 检查每个服务的健康状态
                for service in self.services.values():
                    # 这里可以添加实际的健康检查逻辑
                    # 比如发送一个简单的请求来测试服务是否响应

                    # 简单的健康检查：如果连续失败次数太多，暂时禁用服务
                    if service.consecutive_failures >= self.max_consecutive_failures:
                        if time.time() - service.last_used > self.circuit_breaker_timeout:
                            # 熔断器超时，重置连续失败计数
                            service.consecutive_failures = 0
                            service.status = AIServiceStatus.HEALTHY
                            logger.info(f"Service {service.name} circuit breaker reset")

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                await asyncio.sleep(self.health_check_interval)


# 全局AI负载均衡器实例
ai_load_balancer = AILoadBalancer()
