"""
请求处理中间件
提供请求日志记录、性能监控和用户体验优化
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.logging_config import log_api_request
from app.schemas.responses import success_response, ResponseCode

logger = logging.getLogger(__name__)


class RequestMiddleware:
    """请求处理中间件"""

    def __init__(self):
        self.slow_request_threshold = 2.0  # 慢请求阈值（秒）

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Response]
    ) -> Response:
        """处理请求中间件"""
        start_time = time.time()

        # 记录请求开始
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_ip': self._get_client_ip(request),
                'user_agent': request.headers.get('user-agent', ''),
            }
        )

        try:
            # 处理请求
            response = await call_next(request)
            process_time = time.time() - start_time

            # 记录请求完成
            self._log_request_completion(request, response, process_time)

            # 为成功响应添加处理时间头
            if isinstance(response, JSONResponse):
                response.headers['X-Process-Time'] = '.3f'
                response.headers['X-API-Version'] = '2.0'

                # 如果处理时间过长，添加警告头
                if process_time > self.slow_request_threshold:
                    response.headers['X-Slow-Request'] = 'true'
                    logger.warning(
                        f"Slow request detected: {request.method} {request.url.path} took {process_time:.3f}s",
                        extra={
                            'method': request.method,
                            'path': request.url.path,
                            'process_time': process_time,
                            'client_ip': self._get_client_ip(request),
                        }
                    )

            return response

        except Exception as e:
            # 记录请求失败
            process_time = time.time() - start_time
            self._log_request_failure(request, e, process_time)
            raise

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先使用X-Forwarded-For头（反向代理场景）
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # X-Forwarded-For可能包含多个IP，取第一个
            return forwarded_for.split(',')[0].strip()

        # 其次使用X-Real-IP头
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # 最后使用request.client.host
        return request.client.host if request.client else 'unknown'

    def _log_request_completion(
        self,
        request: Request,
        response: Response,
        process_time: float
    ):
        """记录请求完成"""
        log_api_request(
            logger=logger,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time,
            user_agent=request.headers.get('user-agent'),
            content_length=response.headers.get('content-length')
        )

    def _log_request_failure(
        self,
        request: Request,
        error: Exception,
        process_time: float
    ):
        """记录请求失败"""
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'process_time': process_time,
                'error': str(error),
                'error_type': type(error).__name__,
                'client_ip': self._get_client_ip(request),
            },
            exc_info=True
        )


# 创建中间件实例
request_middleware = RequestMiddleware()
