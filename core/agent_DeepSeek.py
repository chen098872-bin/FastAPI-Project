"""
DeepSeek AI 集成模块
提供智能姓名生成功能，支持重试和超时控制
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any

from fastapi import HTTPException
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.schemas.agent import NameResultSchema
from app.schemas.name import NameIn
from app.core.logging_config import log_ai_request
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


# 延迟初始化LLM，在实际使用时再检查API密钥
_llm = None

def _get_deepseek_llm():
    """获取DeepSeek LLM实例（延迟初始化）"""
    global _llm
    if _llm is None:
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY环境变量未设置，无法使用DeepSeek AI服务")
        _llm = ChatDeepSeek(
            model=settings.DEEPSEEK_MODEL,
            api_key=SecretStr(settings.DEEPSEEK_API_KEY),
            temperature=settings.DEEPSEEK_TEMPERATURE,
            max_tokens=settings.DEEPSEEK_MAX_TOKENS,
            timeout=settings.DEEPSEEK_TIMEOUT,
        )
    return _llm

# 创建一个代理对象来延迟初始化
class _DeepSeekLLMProxy:
    def __getattr__(self, name):
        return getattr(_get_deepseek_llm(), name)

# 使用代理对象，这样在导入时不会初始化
llm = _DeepSeekLLMProxy()

# 2. 优化 System Prompt（起名）
# 核心修改：
# - 明确要求生成 "一组（2个）" 名字
# - 增加 "风格多样化" 的具体定义（自然、古韵、现代、美德）
# - 强调 "结构规范" (姓与名分离)
system_prompt = """
你是一位精通汉语言文学、音韵学与美学的资深命名专家。你的任务是为用户提供 **一组（2个）** 风格迥异、内涵丰富的名字。

请严格遵循以下原则：
1. **风格多样化**：不要局限于一种风格。生成的2个名字中，必须包含不同的侧重，务必拓宽取材范围：
   - **自然意象**：取自山川河流、草木星辰（如：云、溪、林、星）。
   - **经典古韵**：取自《诗经》《楚辞》、唐诗宋词等。
   - **现代审美**：注重音律优美，字形简洁，适合现代社交传播。
   - **美好品质**：象征智慧、勇敢、善良、快乐等。

2. **拒绝平庸**：严禁使用“子涵”、“梓轩”、“欣怡”等过于大众化的“网红名”。
3. **发音优美**：严格把控声调搭配（如平仄平、仄平仄），朗朗上口，避免谐音梗。
4. **结构规范**：严格区分“姓”与“名”。输出 Schema 中的 `given_name` 字段**不应**包含姓氏。
"""

name_agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    response_format=NameResultSchema,
)


async def generate_names(name_info: NameIn) -> NameResultSchema:
    """生成候选姓名列表"""
    # 3. 优化 User Prompt
    # 增加【执行指令】，强制要求数量和格式
    prompt = (
        f"用户姓氏是：{name_info.surname}，"
        f"性别是：{name_info.gender}，"
        f"名字（不含姓氏）的字数严格限制为：{name_info.length} 个字。"
        f"其他个性化要求：{name_info.other}。\n\n"
        f"【执行指令】：\n"
        f"1. 请务必一次性生成 **2个** 不同的名字供用户选择，少于2个是不合格的。\n"
        f"2. 这2个名字的来源和风格要有明显的区别（不要全是古文，也不要全是现代风）。\n"
        f"3. 严禁生成这些字：{'、'.join(name_info.exclude)}。\n"
        f"4. 必须严格按照 NameSchema 格式输出，`given_name` 字段不要包含姓氏。"
    )

    @retry(
        stop=stop_after_attempt(settings.AI_MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.AI_RETRY_BACKOFF),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"DeepSeek name generation failed (attempt {retry_state.attempt_number}/{settings.AI_MAX_RETRIES}), "
            f"retrying in {retry_state.next_action.sleep:.1f} seconds. Error: {retry_state.outcome.exception()}"
        )
    )
    async def _invoke_with_retry() -> NameResultSchema:
        """带重试的AI调用"""
        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                name_agent.ainvoke({
                    "messages": [{
                        "role": "user",
                        "content": prompt,
                    }]
                }),
                timeout=settings.DEEPSEEK_TIMEOUT
            )

            duration = time.time() - start_time
            log_ai_request(
                logger=logger,
                model=settings.DEEPSEEK_MODEL,
                prompt_length=len(prompt),
                response_length=len(str(result.get("structured_response", ""))),
                duration=duration,
                success=True,
                operation="generate_names"
            )

            return result["structured_response"]

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_ai_request(
                logger=logger,
                model=settings.DEEPSEEK_MODEL,
                duration=duration,
                success=False,
                error="Request timeout",
                operation="generate_names"
            )
            raise HTTPException(
                status_code=504,
                detail="AI服务响应超时，请稍后重试"
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            # 检查是否是网络超时相关的错误
            if "ReadTimeoutException" in error_msg or "timeout" in error_msg.lower():
                log_ai_request(
                    logger=logger,
                    model=settings.DEEPSEEK_MODEL,
                    duration=duration,
                    success=False,
                    error=f"Network timeout: {error_msg}",
                    operation="generate_names"
                )
                raise HTTPException(
                    status_code=504,
                    detail="网络请求超时，请检查网络连接后重试"
                )
            else:
                log_ai_request(
                    logger=logger,
                    model=settings.DEEPSEEK_MODEL,
                    duration=duration,
                    success=False,
                    error=error_msg,
                    operation="generate_names"
                )
                logger.error(f"DeepSeek generate names error: {e}")
                raise

    try:
        return await _invoke_with_retry()
    except Exception as e:
        logger.error(f"All retry attempts failed for DeepSeek generate names: {e}")
        # 抛出异常而不是返回无效数据，让调用方处理
        raise HTTPException(
            status_code=503,
            detail="AI服务暂时不可用，请稍后重试"
        )

# async def main():
#     name_info = NameIn(
#         surname="张",
#         gender='女',
#         length="两字"
#     )
#     names = await generate_names(name_info)
#
# if __name__ == '__main__':
#     asyncio.run(main())