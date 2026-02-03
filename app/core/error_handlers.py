"""
统一错误处理中间件
提供用户友好的错误响应和详细的错误日志
"""

import logging
import traceback
from typing import Any, Dict, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.schemas.responses import error_response, ResponseCode
from app.core.logging_config import log_api_request

logger = logging.getLogger(__name__)


class ErrorHandler:
    """统一错误处理器"""

    @staticmethod
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        """处理HTTP异常"""
        # 记录错误详情
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                'status_code': exc.status_code,
                'detail': exc.detail,
                'path': str(request.url),
                'method': request.method,
                'client_ip': request.client.host if request.client else None,
            }
        )

        # 根据状态码返回用户友好的消息
        if exc.status_code == 401:
            message = "身份验证失败，请重新登录"
        elif exc.status_code == 403:
            message = "权限不足，访问被拒绝"
        elif exc.status_code == 404:
            message = "请求的资源不存在"
        elif exc.status_code == 429:
            message = "请求过于频繁，请稍后再试"
        elif exc.status_code >= 500:
            message = "服务器内部错误，请稍后重试"
        else:
            message = exc.detail

        error_resp = error_response(
            code=ResponseCode(exc.status_code),
            message=message,
            details={
                'path': str(request.url),
                'method': request.method
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_resp.dict()
        )

    @staticmethod
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理请求验证错误"""
        logger.warning(
            "Request validation error",
            extra={
                'path': str(request.url),
                'method': request.method,
                'errors': exc.errors(),
                'client_ip': request.client.host if request.client else None,
            }
        )

        # 格式化验证错误信息
        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(x) for x in error.get("loc", []))
            formatted_errors.append({
                'field': field_path,
                'message': error.get('msg', '未知错误'),
                'error_type': error.get('type', 'validation_error')
            })

        error_resp = error_response(
            code=ResponseCode.UNPROCESSABLE_ENTITY,
            message="请求参数格式错误，请检查输入信息",
            errors=formatted_errors,
            details={
                'path': str(request.url),
                'method': request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_resp.dict()
        )

    @staticmethod
    async def handle_pydantic_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        """处理Pydantic验证错误"""
        logger.warning(
            "Pydantic validation error",
            extra={
                'path': str(request.url),
                'method': request.method,
                'errors': exc.errors(),
                'client_ip': request.client.host if request.client else None,
            }
        )

        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(x) for x in error.get("loc", []))
            formatted_errors.append({
                'field': field_path,
                'message': error.get('msg', '数据格式错误'),
                'error_type': error.get('type', 'validation_error')
            })

        error_resp = error_response(
            code=ResponseCode.UNPROCESSABLE_ENTITY,
            message="数据格式错误，请检查输入内容",
            errors=formatted_errors
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_resp.dict()
        )

    @staticmethod
    async def handle_sqlalchemy_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """处理数据库错误"""
        logger.error(
            f"Database error: {type(exc).__name__}: {str(exc)}",
            extra={
                'path': str(request.url),
                'method': request.method,
                'error_type': type(exc).__name__,
                'error_message': str(exc),
                'client_ip': request.client.host if request.client else None,
            },
            exc_info=True
        )

        # 不要暴露数据库内部错误给用户
        error_resp = error_response(
            code=ResponseCode.INTERNAL_SERVER_ERROR,
            message="数据库操作失败，请稍后重试",
            details={
                'error_type': 'database_error',
                'path': str(request.url)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.dict()
        )

    @staticmethod
    async def handle_ai_service_error(request: Request, exc: Exception) -> JSONResponse:
        """处理AI服务相关错误"""
        if "AI服务" in str(exc) or "ai" in str(exc).lower():
            logger.warning(
                f"AI service error: {type(exc).__name__}: {str(exc)}",
                extra={
                    'path': str(request.url),
                    'method': request.method,
                    'error_type': type(exc).__name__,
                    'client_ip': request.client.host if request.client else None,
                }
            )

            error_resp = error_response(
                code=ResponseCode.SERVICE_UNAVAILABLE,
                message="AI服务暂时不可用，请稍后重试",
                details={
                    'service': 'ai_generation',
                    'retry_after': 30  # 建议30秒后重试
                }
            )

            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=error_resp.dict(),
                headers={'Retry-After': '30'}
            )

        # 如果不是AI服务错误，继续传递
        raise exc

    @staticmethod
    async def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
        """处理通用异常"""
        # 特殊处理ResponseValidationError，直接抛出以显示完整错误信息
        if type(exc).__name__ == 'ResponseValidationError':
            print("="*80)
            print("RESPONSE VALIDATION ERROR DETAILS:")
            print(f"Error: {str(exc)}")
            print(f"Path: {request.url}")
            print(f"Method: {request.method}")
            try:
                errors = exc.errors() if callable(getattr(exc, 'errors', None)) else []
                print(f"Validation Errors: {errors}")
            except Exception as e:
                print(f"Could not get validation errors: {e}")
            print(f"Body: {getattr(exc, 'body', 'N/A')}")
            print("="*80)
            # 重新抛出异常，让FastAPI显示完整的错误信息
            raise exc

        # 记录详细错误信息
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            extra={
                'path': str(request.url),
                'method': request.method,
                'error_type': type(exc).__name__,
                'error_message': str(exc),
                'client_ip': request.client.host if request.client else None,
            },
            exc_info=True
        )

        # 为用户提供友好的错误信息
        error_resp = error_response(
            code=ResponseCode.INTERNAL_SERVER_ERROR,
            message="服务器遇到问题，请稍后重试。如问题持续，请联系客服",
            details={
                'error_id': f"{type(exc).__name__}_{hash(str(exc)) % 10000:04d}",
                'timestamp': __import__('datetime').datetime.now().isoformat(),
                'path': str(request.url)
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.dict()
        )

    @staticmethod
    def create_error_response(
        status_code: int,
        message: str,
        errors: list = None,
        details: dict = None
    ) -> JSONResponse:
        """创建标准错误响应"""
        error_resp = error_response(
            code=ResponseCode(status_code),
            message=message,
            errors=errors,
            details=details
        )

        return JSONResponse(
            status_code=status_code,
            content=error_resp.dict()
        )


# 创建全局错误处理器实例
error_handler = ErrorHandler()
