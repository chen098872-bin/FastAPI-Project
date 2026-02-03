"""
企业起名和产品起名业务逻辑模块
支持重试和超时控制
"""

import asyncio
import os
import time
import logging
from typing import Optional

from langchain.agents import create_agent
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.agent_DeepSeek import llm
from app.core.logging_config import log_ai_request
from app.schemas.agent import CompanyNameResultSchema, ProductNameResultSchema
from app.schemas.name import CompanyNameIn, ProductNameIn

logger = logging.getLogger(__name__)

# AI模型配置
AI_CONFIG = {
    "MAX_RETRIES": int(os.getenv("AI_MAX_RETRIES", "3")),
    "RETRY_BACKOFF": float(os.getenv("AI_RETRY_BACKOFF", "1.0")),
    "TIMEOUT": int(os.getenv("AI_TIMEOUT", "30")),
}

# ========== 企业起名 Agent ==========
company_system_prompt = """
你是一位资深的企业命名专家，精通品牌策划、市场营销和商业命名。你的任务是为用户提供专业、有创意、符合商业规范的企业名称。

请严格遵循以下原则：
1. **行业匹配**：名称要符合所属行业特点，体现行业属性。
2. **品牌价值**：名称要有良好的品牌联想，易于建立品牌形象。
3. **商业规范**：符合工商注册规范，避免禁用词汇。
4. **易于记忆**：名称要朗朗上口，便于传播和记忆。
5. **独特性**：避免与知名品牌过于相似，要有独特性。
6. **国际化考虑**：如需国际化，考虑英文翻译和发音。

请为每个名称提供：
- 名称寓意和含义
- 名称优势说明
- 适合的行业或领域
"""

company_agent = create_agent(
    model=llm,
    system_prompt=company_system_prompt,
    response_format=CompanyNameResultSchema,
)


@retry(
    stop=stop_after_attempt(AI_CONFIG["MAX_RETRIES"]),
    wait=wait_exponential(multiplier=AI_CONFIG["RETRY_BACKOFF"]),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: logger.warning(
        f"Company name generation failed, retrying in {retry_state.next_action.sleep} seconds. "
        f"Attempt {retry_state.attempt_number}/{AI_CONFIG['MAX_RETRIES']}"
    )
)
async def _invoke_company_agent_with_retry(prompt: str) -> CompanyNameResultSchema:
    """带重试的企业起名AI调用"""
    start_time = time.time()

    try:
        result = await asyncio.wait_for(
            company_agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": prompt,
                }]
            }),
            timeout=AI_CONFIG["TIMEOUT"]
        )

        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            prompt_length=len(prompt),
            response_length=len(str(result.get("structured_response", ""))),
            duration=duration,
            success=True,
            operation="generate_company_names"
        )

        return result["structured_response"]

    except asyncio.TimeoutError:
        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            duration=duration,
            success=False,
            error="Request timeout",
            operation="generate_company_names"
        )
        raise HTTPException(
            status_code=504,
            detail="企业起名服务响应超时，请稍后重试"
        )

    except Exception as e:
        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            duration=duration,
            success=False,
            error=str(e),
            operation="generate_company_names"
        )
        logger.error(f"Company name generation error: {e}")
        raise


async def generate_company_names(company_info: CompanyNameIn) -> CompanyNameResultSchema:
    """生成企业名称"""
    prompt = (
        f"【企业信息】\n"
        f"所属行业：{company_info.industry}\n"
        f"企业类型：{company_info.company_type}\n"
        f"经营范围：{company_info.business_scope}\n"
        f"市场定位：{company_info.positioning or '未指定'}\n"
        f"字数要求：{company_info.length}\n"
        f"风格偏好：{company_info.style or '未指定'}\n"
        f"排除词汇：{', '.join(company_info.exclude) if company_info.exclude else '无'}\n\n"
        f"【任务要求】\n"
        f"1. 请生成 3-5 个企业名称候选方案。\n"
        f"2. 每个名称都要有明确的寓意和商业价值。\n"
        f"3. 名称要符合工商注册规范，避免使用禁用词。\n"
        f"4. 考虑名称的易读性、记忆性和传播性。\n"
        f"5. 如果指定了风格，要符合风格要求。\n"
        f"6. 严禁使用排除的词汇。\n"
    )

    try:
        return await _invoke_company_agent_with_retry(prompt)
    except Exception as e:
        logger.error(f"All retry attempts failed for company name generation: {e}")
        # 返回安全的默认响应，避免服务崩溃
        return CompanyNameResultSchema(names=[])


# ========== 产品起名 Agent ==========
product_system_prompt = """
你是一位资深的产品命名专家，精通产品策划、用户体验和市场营销。你的任务是为用户提供有创意、有吸引力、符合产品定位的产品名称。

请严格遵循以下原则：
1. **产品匹配**：名称要准确反映产品功能和特点。
2. **用户导向**：考虑目标用户群体的喜好和认知习惯。
3. **市场定位**：名称要符合产品的市场定位（高端、性价比、创新等）。
4. **易于传播**：名称要简洁易记，便于口碑传播。
5. **差异化**：避免与竞品名称过于相似，要有独特性。
6. **情感共鸣**：名称要有情感吸引力，能引起用户共鸣。

请为每个名称提供：
- 名称寓意和含义
- 名称特点说明
- 目标用户群体
- 市场定位
"""

product_agent = create_agent(
    model=llm,
    system_prompt=product_system_prompt,
    response_format=ProductNameResultSchema,
)


@retry(
    stop=stop_after_attempt(AI_CONFIG["MAX_RETRIES"]),
    wait=wait_exponential(multiplier=AI_CONFIG["RETRY_BACKOFF"]),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: logger.warning(
        f"Product name generation failed, retrying in {retry_state.next_action.sleep} seconds. "
        f"Attempt {retry_state.attempt_number}/{AI_CONFIG['MAX_RETRIES']}"
    )
)
async def _invoke_product_agent_with_retry(prompt: str) -> ProductNameResultSchema:
    """带重试的产品起名AI调用"""
    start_time = time.time()

    try:
        result = await asyncio.wait_for(
            product_agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": prompt,
                }]
            }),
            timeout=AI_CONFIG["TIMEOUT"]
        )

        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            prompt_length=len(prompt),
            response_length=len(str(result.get("structured_response", ""))),
            duration=duration,
            success=True,
            operation="generate_product_names"
        )

        return result["structured_response"]

    except asyncio.TimeoutError:
        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            duration=duration,
            success=False,
            error="Request timeout",
            operation="generate_product_names"
        )
        raise HTTPException(
            status_code=504,
            detail="产品起名服务响应超时，请稍后重试"
        )

    except Exception as e:
        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            duration=duration,
            success=False,
            error=str(e),
            operation="generate_product_names"
        )
        logger.error(f"Product name generation error: {e}")
        raise


async def generate_product_names(product_info: ProductNameIn) -> ProductNameResultSchema:
    """生成产品名称"""
    prompt = (
        f"【产品信息】\n"
        f"产品类型：{product_info.product_type}\n"
        f"产品功能：{product_info.product_function}\n"
        f"目标用户：{product_info.target_audience or '未指定'}\n"
        f"市场定位：{product_info.market_positioning or '未指定'}\n"
        f"字数要求：{product_info.length}\n"
        f"风格偏好：{product_info.style or '未指定'}\n"
        f"排除词汇：{', '.join(product_info.exclude) if product_info.exclude else '无'}\n\n"
        f"【任务要求】\n"
        f"1. 请生成 3-5 个产品名称候选方案。\n"
        f"2. 每个名称都要准确反映产品特点和功能。\n"
        f"3. 名称要有吸引力，能引起目标用户的兴趣。\n"
        f"4. 考虑名称在不同场景下的使用（APP图标、广告语、包装等）。\n"
        f"5. 如果指定了风格，要符合风格要求。\n"
        f"6. 严禁使用排除的词汇。\n"
    )

    try:
        return await _invoke_product_agent_with_retry(prompt)
    except Exception as e:
        logger.error(f"All retry attempts failed for product name generation: {e}")
        # 返回安全的默认响应，避免服务崩溃
        return ProductNameResultSchema(names=[])

