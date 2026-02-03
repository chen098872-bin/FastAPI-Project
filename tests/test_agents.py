"""
测试AI代理模块
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from app.schemas.name import NameIn
from app.core.config import Settings


class TestDeepSeekAgent:
    """测试DeepSeek代理"""

    def test_missing_api_key_raises_error(self):
        """测试缺少API密钥时抛出错误"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.DEEPSEEK_API_KEY = ""

            with pytest.raises(ValueError, match="DEEPSEEK_API_KEY环境变量未设置"):
                from app.core.agent_DeepSeek import llm  # noqa: F401

    def test_agent_with_valid_config(self):
        """测试有效配置下的代理初始化"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.DEEPSEEK_API_KEY = "test_key"
            mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
            mock_settings.DEEPSEEK_TEMPERATURE = 1.2
            mock_settings.DEEPSEEK_MAX_TOKENS = 2000
            mock_settings.DEEPSEEK_TIMEOUT = 30

            from app.core.agent_DeepSeek import llm
            assert llm is not None

    @pytest.mark.asyncio
    async def test_generate_names_failure_handling(self):
        """测试姓名生成失败时的错误处理"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.DEEPSEEK_API_KEY = "test_key"
            mock_settings.AI_MAX_RETRIES = 1
            mock_settings.DEEPSEEK_TIMEOUT = 1

            from app.core.agent_DeepSeek import generate_names

            name_info = NameIn(
                surname="张",
                gender="男",
                length="两字"
            )

            # 应该抛出HTTPException而不是返回无效数据
            with pytest.raises(HTTPException) as exc_info:
                await generate_names(name_info)

            assert exc_info.value.status_code == 503


class TestQwenAgent:
    """测试Qwen代理"""

    def test_missing_api_key_raises_error(self):
        """测试缺少API密钥时抛出错误"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.ALIBABA_API_KEY = ""

            with pytest.raises(ValueError, match="ALIBABA_API_KEY环境变量未设置"):
                from app.core.agent_Qwen import llm  # noqa: F401

    def test_agent_with_valid_config(self):
        """测试有效配置下的代理初始化"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.ALIBABA_API_KEY = "test_key"
            mock_settings.ALIBABA_MODEL = "qwen-plus"
            mock_settings.ALIBABA_BASE_URL = "https://test.com"
            mock_settings.ALIBABA_TEMPERATURE = 1.2

            from app.core.agent_Qwen import llm
            assert llm is not None

    @pytest.mark.asyncio
    async def test_generate_names_failure_handling(self):
        """测试姓名生成失败时的错误处理"""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.ALIBABA_API_KEY = "test_key"
            mock_settings.AI_MAX_RETRIES = 1
            mock_settings.ALIBABA_TIMEOUT = 1

            from app.core.agent_Qwen import generate_names_text

            name_info = NameIn(
                surname="张",
                gender="男",
                length="两字"
            )

            # 应该抛出HTTPException而不是返回无效数据
            with pytest.raises(HTTPException) as exc_info:
                await generate_names_text(name_info)

            assert exc_info.value.status_code == 503


class TestAIServiceFallback:
    """测试AI服务降级"""

    @pytest.mark.asyncio
    async def test_service_unavailable_error(self):
        """测试服务不可用时的错误处理"""
        # 这个测试确保当AI服务完全不可用时，返回适当的错误而不是崩溃

        # 模拟网络连接失败的情况
        with patch('app.core.agent_DeepSeek.name_agent') as mock_agent:
            mock_agent.ainvoke = AsyncMock(side_effect=Exception("Network error"))

            from app.core.agent_DeepSeek import generate_names

            name_info = NameIn(
                surname="张",
                gender="男",
                length="两字"
            )

            with pytest.raises(HTTPException) as exc_info:
                await generate_names(name_info)

            assert exc_info.value.status_code == 503
            assert "暂时不可用" in exc_info.value.detail
