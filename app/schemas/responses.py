"""
统一响应格式定义
提供标准化的API响应结构和错误处理
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class ResponseCode(int, Enum):
    """响应状态码"""
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class ResponseStatus(str, Enum):
    """响应状态"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseModel):
    """基础响应模型"""
    code: ResponseCode = Field(..., description="响应状态码")
    status: ResponseStatus = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    timestamp: str = Field(default_factory=lambda: __import__('datetime').datetime.now().isoformat(),
                          description="响应时间戳")

    class Config:
        use_enum_values = True


class SuccessResponse(BaseResponse):
    """成功响应"""
    code: ResponseCode = ResponseCode.SUCCESS
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: Optional[Any] = Field(None, description="响应数据")


class ErrorResponse(BaseResponse):
    """错误响应"""
    status: ResponseStatus = ResponseStatus.ERROR
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="详细错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="额外的错误详情")


class PaginatedResponse(SuccessResponse):
    """分页响应"""
    data: Dict[str, Any] = Field(..., description="分页数据")
    pagination: Dict[str, Union[int, bool]] = Field(..., description="分页信息")

    @classmethod
    def create(
        cls,
        items: List[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "获取成功"
    ) -> "PaginatedResponse":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size

        return cls(
            message=message,
            data={"items": items},
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )


class AIStatusResponse(SuccessResponse):
    """AI服务状态响应"""
    data: Dict[str, Dict[str, Any]] = Field(..., description="AI服务状态数据")


# 用户友好的错误消息映射
ERROR_MESSAGES = {
    ResponseCode.BAD_REQUEST: "请求参数错误，请检查输入信息",
    ResponseCode.UNAUTHORIZED: "身份验证失败，请重新登录",
    ResponseCode.FORBIDDEN: "权限不足，访问被拒绝",
    ResponseCode.NOT_FOUND: "请求的资源不存在",
    ResponseCode.CONFLICT: "请求冲突，资源已存在或状态冲突",
    ResponseCode.UNPROCESSABLE_ENTITY: "请求数据格式错误",
    ResponseCode.INTERNAL_SERVER_ERROR: "服务器内部错误，请稍后重试",
    ResponseCode.BAD_GATEWAY: "网关错误，请稍后重试",
    ResponseCode.SERVICE_UNAVAILABLE: "服务暂时不可用，请稍后重试",
    ResponseCode.GATEWAY_TIMEOUT: "请求超时，请稍后重试",
}


class APIResponse:
    """API响应工具类"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: ResponseCode = ResponseCode.SUCCESS
    ) -> SuccessResponse:
        """创建成功响应"""
        return SuccessResponse(
            code=code,
            message=message,
            data=data
        )

    @staticmethod
    def error(
        code: ResponseCode,
        message: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """创建错误响应"""
        return ErrorResponse(
            code=code,
            message=message or ERROR_MESSAGES.get(code, "未知错误"),
            errors=errors,
            details=details
        )

    @staticmethod
    def paginated(
        items: List[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "获取成功"
    ) -> PaginatedResponse:
        """创建分页响应"""
        return PaginatedResponse.create(items, page, page_size, total, message)


# 便捷函数
def success_response(data: Any = None, message: str = "操作成功") -> SuccessResponse:
    """便捷的成功响应函数"""
    return APIResponse.success(data, message)


def error_response(
    code: ResponseCode,
    message: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """便捷的错误响应函数"""
    return APIResponse.error(code, message, errors, details)


def paginated_response(
    items: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "获取成功"
) -> PaginatedResponse:
    """便捷的分页响应函数"""
    return APIResponse.paginated(items, page, page_size, total, message)
