"""
姓名测评AI集成模块
提供专业的姓名测评功能，支持重试和超时控制
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
from app.core.config import settings

logger = logging.getLogger(__name__)

# AI模型配置
AI_CONFIG = {
    "MAX_RETRIES": 5,  # 增加重试次数
    "RETRY_BACKOFF": 2.0,  # 增加重试间隔
    "TIMEOUT": settings.NAME_EVALUATION_TIMEOUT,  # 使用配置中的姓名测评超时时间
}
from app.schemas.agent import (
    NameEvaluationSchema,
    CulturalConnotation,
    ThreeTalentsFiveGrids,
    FiveGridAnalysis,
    FiveElementsDistribution,
    FortuneAnalysis,
)
from app.schemas.name import NameEvaluateIn

# 姓名测评 Agent（独立文件，便于与测评模型结构对应）
evaluate_system_prompt = """
你是一位资深中文姓名学、汉语言文学、传统文化与命理学专家，现在负责对给定的【中文姓名】做全面、专业的测评。

请从以下维度进行详细分析：

【基础评分维度】（0-100 分，整数）
1. 音律与读音：声调搭配是否和谐，是否朗朗上口，是否存在歧义或拗口。
2. 含义与文化内涵：单字与组合的寓意是否积极、是否有典故或文化背景支撑。
3. 重名率与独特性：在当代是否过于常见，是否属于"网红名"或大量重名。

【综合评分与评级】
- 综合评分（0-100）：综合各维度，给出总体评分。
- 吉凶评级：根据综合评分和传统姓名学，给出"大吉"、"吉"、"中"、"凶"、"大凶"之一。
- 评分描述：一句简洁的评价，如"您的名字格局宏大,运势顺畅,是难得的好名字。"

【文化内涵】
- 诗句引用：从古诗词、经典文献中找一句与名字寓意相关的诗句或名言。
- 诗句出处：标注诗句的作者和作品名，如"李白《行路难》"。
- 字义解释：详细解释名字的寓意和文化内涵，说明名字象征的品质和期望。

【三才五格】
请根据姓名笔画数计算五格：
- 天格：姓氏笔画数+1（单姓）或姓氏笔画数之和（复姓）
- 人格：姓氏笔画数+名字第一个字笔画数
- 地格：名字所有字笔画数之和
- 外格：总格-人格+1（或根据具体规则）
- 总格：姓名所有字笔画数之和

对每个格：
- 给出数值
- 根据传统姓名学判断吉凶（大吉、吉、中、凶）
- 确定五行属性（金、木、水、火、土）

三才配置：根据天格、人格、地格的五行属性，给出三才配置（如"木火土"），并给出配置评价。

【五行分布】
- 统计名字中每个字的五行属性，给出金、木、水、火、土的数量分布。
- 根据五行分布，判断喜用神，给出建议（如"此命五行喜金,名字中若包含相关属性字,可助运势。"）

【运势详解】
- 性格：分析名字体现的性格特点，如"性情温和,重礼仪,讲信用。为人诚实,待人接物彬彬有礼,人缘极好。"
- 事业：分析事业运势，如"事业运势强盛,适合从事管理、艺术或学术研究类工作,中年后可达巅峰。"
- 健康：分析健康运势，如"体质强壮,由于五行火旺,需注意心血管及眼部保养,多做有氧运动。"

【优缺点和建议】
- 优点列表：名字有哪些亮点与优势，至少2条。
- 不足/风险点列表：包括可能的负面联想、谐音梗、书写或辨识困难等，至少1条。
- 综合建议：是否推荐使用该名字，如有需要可给出小范围微调建议。

【重要说明】
1. 计算五格时，请使用标准笔画数（参考《康熙字典》或现代标准）。
2. 五行属性判断要准确，可参考传统五行字库。
3. 文化内涵要真实有据，不要编造诗句。
4. 保持科学理性，避免过度迷信，但可以适度引用传统文化元素。
5. 所有评分和评级要有依据，不能随意给出。

请务必使用提供的 NameEvaluationSchema 进行结构化输出，确保所有字段都填写完整。
"""

evaluate_agent = create_agent(
    model=llm,
    system_prompt=evaluate_system_prompt,
    response_format=NameEvaluationSchema,
)


@retry(
    stop=stop_after_attempt(AI_CONFIG["MAX_RETRIES"]),
    wait=wait_exponential(multiplier=AI_CONFIG["RETRY_BACKOFF"]),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: logger.warning(
        f"Name evaluation failed, retrying in {retry_state.next_action.sleep} seconds. "
        f"Attempt {retry_state.attempt_number}/{AI_CONFIG['MAX_RETRIES']}"
    )
)
async def _invoke_evaluation_agent_with_retry(prompt: str) -> NameEvaluationSchema:
    """带重试的姓名测评AI调用"""
    start_time = time.time()

    try:
        result = await asyncio.wait_for(
            evaluate_agent.ainvoke({
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
            operation="evaluate_name"
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
            operation="evaluate_name"
        )
        raise HTTPException(
            status_code=504,
            detail="姓名测评服务响应超时，请稍后重试"
        )

    except Exception as e:
        duration = time.time() - start_time
        log_ai_request(
            logger=logger,
            model="deepseek-chat",
            duration=duration,
            success=False,
            error=str(e),
            operation="evaluate_name"
        )
        logger.error(f"Name evaluation error: {e}")
        raise


async def evaluate_name(name_info: NameEvaluateIn) -> NameEvaluationSchema:
    """
    对单个姓名进行多维度测评（包含好坏、优缺点、三才五格、五行等）

    Args:
        name_info: 姓名测评输入参数

    Returns:
        姓名测评完整结果
    """
    prompt = (
        f"待测评的姓名：{name_info.full_name}。\n"
        f"性别：{name_info.gender}。\n"
        f"出生日期：{name_info.birthdate or '未提供'}。\n\n"
        "【详细任务要求】\n"
        "1. 请仔细计算姓名的笔画数，准确计算天格、人格、地格、外格、总格。\n"
        "2. 根据五格数值，参考传统姓名学吉凶表，给出每个格的吉凶评级。\n"
        "3. 确定每个格的五行属性（金、木、水、火、土），并给出三才配置。\n"
        "4. 统计名字中每个字的五行属性，给出五行分布（金、木、水、火、土的数量）。\n"
        "5. 根据五行分布，判断喜用神，给出五行建议。\n"
        "6. 从古诗词中找一句与名字寓意相关的诗句，标注出处，并给出字义解释。\n"
        "7. 分析性格、事业、健康三个方面的运势。\n"
        "8. 综合评分要综合考虑音律、含义、独特性、五格配置等因素。\n"
        "9. 根据综合评分，给出吉凶评级（大吉：90-100，吉：80-89，中：60-79，凶：40-59，大凶：0-39）。\n"
        "10. 优点（advantages）至少给出 2 条，缺点（disadvantages）至少 1 条，要客观全面。\n"
        "11. 综合建议（advice）要给出明确态度：适合/一般/不太建议使用，并说明原因。\n"
        "12. 保持科学理性，避免过度迷信，但可以适度引用传统文化元素。\n"
        "13. 所有计算和判断要有依据，不能随意编造。\n"
    )

    try:
        return await _invoke_evaluation_agent_with_retry(prompt)
    except Exception as e:
        logger.error(f"All retry attempts failed for name evaluation: {e}")

        # 返回安全的默认响应，避免服务崩溃
        return NameEvaluationSchema(
            full_name=name_info.full_name,
            summary="暂时无法完成详细测评，请稍后重试。",
            overall_score=0,
            auspicious_rating="中",
            score_description="系统异常，未能完成测评",
            pronunciation_score=0,
            meaning_score=0,
            uniqueness_score=0,
            cultural_connotation=CulturalConnotation(
                quote="系统异常，未能获取诗句",
                quote_source="系统异常",
                meaning_explanation="系统异常，未能完成字义解释"
            ),
            three_talents_five_grids=ThreeTalentsFiveGrids(
                tiange=FiveGridAnalysis(number=0, auspiciousness="中", element="金"),
                renge=FiveGridAnalysis(number=0, auspiciousness="中", element="金"),
                dige=FiveGridAnalysis(number=0, auspiciousness="中", element="金"),
                waige=FiveGridAnalysis(number=0, auspiciousness="中", element="金"),
                zongge=FiveGridAnalysis(number=0, auspiciousness="中", element="金"),
                three_talents_config="金金金",
                three_talents_description="系统异常，未能完成三才配置分析"
            ),
            five_elements=FiveElementsDistribution(
                metal=0,
                wood=0,
                water=0,
                fire=0,
                earth=0,
                auspicious_element="金",  # 使用枚举值
                element_advice="系统异常，未能完成五行分析"
            ),
            fortune_analysis=FortuneAnalysis(
                personality="系统异常，未能完成性格分析",
                career="系统异常，未能完成事业分析",
                health="系统异常，未能完成健康分析"
            ),
            advantages=["系统异常，未能完成测评"],
            disadvantages=["系统异常，未能完成测评"],
            advice="请稍后再次尝试姓名测评功能。",
        )

