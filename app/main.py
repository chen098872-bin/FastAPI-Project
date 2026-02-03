"""
FastAPI应用主入口
"""

import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from aiosmtplib import SMTPResponseException

from app.core.logging_config import setup_logging, log_api_request
from app.core.error_handlers import error_handler
from app.core.request_middleware import request_middleware

# 初始化日志配置
logger = setup_logging()
from app.core.deps import get_mail, register_static_files
from app.api.v1.auth_router import router as auth_router
from app.api.v1.name_router import router as name_router
from app.api.v1.user_router import router as user_router
from app.api.v1.favorite_router import router as favorite_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting LLM Chat API server")

    # 检查必需的环境变量
    from app.core.config import settings
    missing_vars = []
    if not settings.DEEPSEEK_API_KEY:
        missing_vars.append("DEEPSEEK_API_KEY")
    if not settings.ALIBABA_API_KEY:
        missing_vars.append("ALIBABA_API_KEY")

    if missing_vars:
        logger.warning(f"⚠️  缺少必需的环境变量: {', '.join(missing_vars)}")
        logger.warning("请在生产环境中设置这些环境变量以启用AI功能")

    # 初始化AI服务负载均衡器（延迟到使用时注册）
    try:
        from app.core.ai_load_balancer import ai_load_balancer
        logger.info("AI load balancer initialized (services will be registered on first use)")
    except Exception as e:
        logger.error(f"Failed to initialize AI load balancer: {e}")

    yield

    # 关闭时的清理工作
    logger.info("Shutting down LLM Chat API server")

    # 取消健康检查任务
    try:
        if 'health_check_task' in locals():
            health_check_task.cancel()
            logger.info("AI service health check stopped")
    except Exception as e:
        logger.error(f"Error stopping health check: {e}")


app = FastAPI(
    title="智能姓名生成服务",
    description="基于AI的智能姓名生成和测评系统",
    version="2.0.0",
    lifespan=lifespan,
)

# 注册静态文件服务（支持头像访问）
register_static_files(app)

# 路由挂载
app.include_router(auth_router, prefix="/api/v1", tags=["认证"])
app.include_router(name_router, prefix="/api/v1", tags=["姓名生成"])
app.include_router(user_router, prefix="/api/v1", tags=["用户管理"])
app.include_router(favorite_router, prefix="/api/v1", tags=["收藏管理"])

# 企业起名收藏路由已移回 name_router.py


# ================= 请求处理中间件 =================

@app.middleware("http")
async def request_processing_middleware(request: Request, call_next):
    """统一的请求处理中间件"""
    return await request_middleware(request, call_next)


# 使用新的统一错误处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    return await error_handler.handle_http_exception(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证错误处理器"""
    return await error_handler.handle_validation_error(request, exc)


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    """ResponseValidationError处理器 - 显示详细信息后抛出"""
    print("="*80)
    print("RESPONSE VALIDATION ERROR HANDLER CALLED")
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

    # 直接重新抛出，让FastAPI显示完整的错误信息
    raise exc


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    # ResponseValidationError现在由专门的处理器处理

    # 首先尝试处理AI服务相关错误
    try:
        return await error_handler.handle_ai_service_error(request, exc)
    except Exception:
        # 如果不是AI服务错误，使用通用错误处理器
        return await error_handler.handle_generic_error(request, exc)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/mail/test")
async def mail_test(
    email: str,
    mail: FastMail = Depends(get_mail),
):
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body=f"hello {email}",
        subtype=MessageType.plain,
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
    return {"message": "邮件发送成功！"}