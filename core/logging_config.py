"""
日志配置模块
提供结构化日志记录和错误处理
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义JSON日志格式器"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # 添加时间戳
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        # 添加日志级别
        log_record['level'] = record.levelname

        # 添加模块信息
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # 添加进程信息
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread


def setup_logging():
    """配置应用日志"""

    # 获取日志级别
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', 'json').lower()

    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # 移除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建格式器
    if log_format == 'json':
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(module)s %(function)s %(line)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 创建文件处理器
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(
        log_dir / 'app.log',
        encoding='utf-8',
        mode='a'  # 追加模式
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 创建错误日志文件处理器
    error_file_handler = logging.FileHandler(
        log_dir / 'error.log',
        encoding='utf-8',
        mode='a'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    root_logger.addHandler(error_file_handler)

    # 配置第三方库日志级别
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('aiosqlite').setLevel(logging.WARNING)
    logging.getLogger('aiomysql').setLevel(logging.WARNING)

    # 设置uvicorn日志
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

    return root_logger


class LoggerMixin:
    """日志混入类，为类提供日志功能"""

    @property
    def logger(self):
        """获取类专用的日志器"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_api_request(logger: logging.Logger, method: str, path: str, user_id: int = None,
                   status_code: int = None, duration: float = None, **extra):
    """记录API请求日志"""
    log_data = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': round(duration * 1000, 2) if duration else None,
        'user_id': user_id,
        **extra
    }

    if status_code and status_code >= 400:
        logger.warning("API request failed", extra=log_data)
    else:
        logger.info("API request completed", extra=log_data)


def log_database_operation(logger: logging.Logger, operation: str, table: str,
                          record_id: Any = None, user_id: int = None, **extra):
    """记录数据库操作日志"""
    log_data = {
        'operation': operation,
        'table': table,
        'record_id': record_id,
        'user_id': user_id,
        **extra
    }

    logger.info("Database operation", extra=log_data)


def log_ai_request(logger: logging.Logger, model: str, prompt_length: int = None,
                  response_length: int = None, duration: float = None,
                  success: bool = True, error: str = None, **extra):
    """记录AI请求日志"""
    log_data = {
        'model': model,
        'prompt_length': prompt_length,
        'response_length': response_length,
        'duration_ms': round(duration * 1000, 2) if duration else None,
        'success': success,
        'error': error,
        **extra
    }

    if success:
        logger.info("AI request completed", extra=log_data)
    else:
        logger.error("AI request failed", extra=log_data)
