import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException, status

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent_DeepSeek import generate_names as generate_names_deepseek
from app.core.agent_Qwen import generate_names_text as generate_names_qwen
from app.core.ai_load_balancer import ai_load_balancer
from app.core.deps import get_session, CurrentUserDep, SessionDep
from app.core.auth import AuthHandler
from app.core.name_evaluation_agent import evaluate_name
from app.core.business_name_agent import (
    generate_company_names,
    generate_product_names,
)
# Note: get_async_session is deprecated, using get_session instead
from app.repositories.repetition_repo import RepetitionRepo
from app.repositories.history_test_repo import NameHistoryRepository
from app.repositories.company_naming_repo import CompanyNamingRepository
from app.repositories.product_naming_repo import ProductNamingRepository
from app.core.api_handlers import api_handler
from app.schemas.name import (
    NameIn,
    NameOut,
    NameEvaluateIn,
    NameEvaluateOut,
    CompanyNameIn,
    CompanyNameOut,
    ProductNameIn,
    ProductNameOut,
    FavoriteRequest,
)
from app.schemas.repetition import RepetitionOut, NameTopOut
from app.schemas.history_test import NameHistoryOut, BatchDeleteHistoryRequest

# 企业起名和产品起名历史记录schema（需要创建）
from typing import Union
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/name")
auth_handler = AuthHandler()


@router.post("", response_model=NameOut)
async def take_names_text(
    data: NameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session=Depends(get_session),
):
    # 使用负载均衡器选择最优AI服务
    name_result = await ai_load_balancer.generate_names(data)
    history_repo = NameHistoryRepository(session)
    await history_repo.create(
        user_id=user_id,
        input_params=data.dict(),
        generated_names=name_result.dict(),
        model_used="load_balanced",  # 使用负载均衡
    )
    return NameOut(names=name_result.names)


@router.post("/text", response_model=NameOut)
async def take_names_text_text(
    data: NameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session=Depends(get_session),
):
    name_result = await generate_names_qwen(data)
    history_repo = NameHistoryRepository(session)
    await history_repo.create(
        user_id=user_id,
        input_params=data.dict(),
        generated_names=name_result.dict(),
        model_used="alibaba",
    )
    return NameOut(names=name_result.names)


@router.post("/evaluate", response_model=NameEvaluateOut)
async def evaluate_name_endpoint(
    data: NameEvaluateIn,
    user_id: int = Depends(auth_handler.auth_access_dependency),
):
    """
    使用大模型对单个姓名进行多维度测评（好坏、优缺点都会给出）
    """
    # 当前版本只调用 LLM 返回测评结果，不做历史记录入库
    result = await evaluate_name(data)
    return result


@router.get("/history", response_model=List[NameHistoryOut])
async def get_name_history(
    page: int = 1,
    page_size: int = 10,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session = Depends(get_session)
):
    history_repo = NameHistoryRepository(session)
    history_list = await history_repo.get_by_user(
        user_id=user_id,
        page=page,
        page_size=page_size
    )
    return history_list

@router.get("/repetition", response_model=RepetitionOut)
async def get_repetition(
    name: str = Query(..., description="名字"),
    gender: str = Query(..., pattern="^(男|女)$", description="性别"),
    region: Optional[str] = Query(None, description="地区"),
    user_id: int = Depends(auth_handler.auth_access_dependency),  # 启用认证
    session: AsyncSession = Depends(get_session)
):
    repo = RepetitionRepo(session)
    return await repo.calculate(name=name, gender=gender, region=region)

@router.get("/top", response_model=List[NameTopOut])
async def get_top_names(
    gender: Optional[str] = None,  # 可选按性别筛选
    limit: int = 10,  # 可选返回数量（默认10）
    session: AsyncSession = Depends(get_session)  # 依赖注入 get_session，参数名统一为 session
):
    """
    获取使用次数最多的前N个名字
    :param gender: 可选性别筛选（“男”/“女”，不填则返回所有性别）
    :param limit: 返回数量（默认10，最大支持50）
    :param session: 数据库会话（由 get_session 依赖提供）
    :return: 名字使用次数TopN列表
    """
    # 校验参数
    if gender and gender not in ["男", "女"]:
        raise HTTPException(status_code=400, detail="gender必须为“男”或“女”")
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="limit必须在1-50之间")

    # 调用仓库层，传递 session（而非 db）
    repo = RepetitionRepo(session)  # 修正：使用 session 作为参数
    result = await repo.get_top_names(gender=gender, limit=limit)
    return result

# ========== 调整顺序：先注册批量删除（/history/batch） ==========
@router.delete("/history/batch", status_code=status.HTTP_200_OK, response_model=Dict[str, int])
async def delete_batch_history_records(
    request: BatchDeleteHistoryRequest,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session)
):
    """批量删除姓名生成历史记录"""
    history_repo = NameHistoryRepository(session)
    deleted_count = await history_repo.delete_batch_history(
        history_ids=request.history_ids,
        user_id=user_id
    )
    return {"deleted_count": deleted_count}

# ========== 后注册单条删除（/history/{history_id}） ==========
# ========== 企业起名接口 ==========
@router.post("/company", response_model=CompanyNameOut)
async def generate_company_name(
    data: CompanyNameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    企业起名接口

    根据行业、经营范围、市场定位等信息，生成专业的企业名称候选方案。
    """
    try:
        # 生成企业名称
        name_result = await generate_company_names(data)

        # 保存到企业起名历史记录
        company_repo = CompanyNamingRepository(session)
        await company_repo.create_history(
            user_id=user_id,
            input_params=data,
            generated_names=name_result.dict(),
            model_used="deepseek-company",
        )

        return CompanyNameOut(names=name_result.names)

    except Exception as e:
        logger.error(f"Failed to generate company names: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="企业起名失败，请稍后重试"
        )


# ========== 产品起名接口 ==========
@router.post("/product", response_model=ProductNameOut)
async def generate_product_name(
    data: ProductNameIn,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    产品起名接口

    根据产品类型、功能、目标用户等信息，生成有吸引力的产品名称候选方案。
    """
    try:
        # 生成产品名称
        name_result = await generate_product_names(data)

        # 保存到产品起名历史记录
        product_repo = ProductNamingRepository(session)
        await product_repo.create_history(
            user_id=user_id,
            input_params=data,
            generated_names=name_result.dict(),
            model_used="deepseek-product",
        )

        return ProductNameOut(names=name_result.names)

    except Exception as e:
        logger.error(f"Failed to generate product names: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="产品起名失败，请稍后重试"
        )


# ========== 企业起名历史记录 ==========
class CompanyHistoryOut(BaseModel):
    """企业起名历史记录输出"""
    id: int
    industry: str
    company_type: str
    business_scope: str
    positioning: Optional[str]
    length: str
    style: Optional[str]
    exclude: List[str]
    generated_names: dict
    model_used: str
    created_at: str


@router.get("/company/history", response_model=List[CompanyHistoryOut])
async def get_company_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    获取企业起名历史记录
    """
    return await api_handler.handle_history_list(
        repository_class=CompanyNamingRepository,
        response_model=CompanyHistoryOut,
        user_id=user_id,
        session=session,
        page=page,
        page_size=page_size,
        operation_name="获取企业起名历史记录"
    )


@router.delete("/company/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_history(
    history_id: int,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    删除企业起名历史记录
    """
    await api_handler.handle_history_delete(
        repository_class=CompanyNamingRepository,
        history_id=history_id,
        user_id=user_id,
        session=session,
        operation_name="删除企业起名历史记录"
    )


# ========== 企业起名收藏 ==========
@router.post("/company-favorite/add", status_code=status.HTTP_201_CREATED, response_model=None)
async def add_company_favorite(
    req: FavoriteRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    添加企业起名到收藏
    """
    favorite = await add_favorite(db, current_user.id, req.history_id)
    result = {"message": "收藏成功", "favorite_id": favorite.id}
    return result


@router.post("/company-favorite/remove", status_code=status.HTTP_200_OK, response_model=None)
async def remove_company_favorite(
    req: FavoriteRequest,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    从收藏中移除企业起名
    """
    await remove_favorite(db, current_user.id, req.history_id)
    return {"message": "取消收藏成功"}


@router.get("/company-favorite/list", status_code=status.HTTP_200_OK)
async def get_company_favorites(
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """
    获取企业起名收藏列表
    """
    return await get_user_favorites(db, current_user.id)


# ========== 产品起名历史记录 ==========
class ProductHistoryOut(BaseModel):
    """产品起名历史记录输出"""
    id: int
    product_type: str
    product_function: str
    target_audience: Optional[str]
    market_positioning: Optional[str]
    length: str
    style: Optional[str]
    exclude: List[str]
    generated_names: dict
    model_used: str
    created_at: str


@router.get("/product/history", response_model=List[ProductHistoryOut])
async def get_product_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    获取产品起名历史记录
    """
    return await api_handler.handle_history_list(
        repository_class=ProductNamingRepository,
        response_model=ProductHistoryOut,
        user_id=user_id,
        session=session,
        page=page,
        page_size=page_size,
        operation_name="获取产品起名历史记录"
    )


@router.delete("/product/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_history(
    history_id: int,
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    删除产品起名历史记录
    """
    await api_handler.handle_history_delete(
        repository_class=ProductNamingRepository,
        history_id=history_id,
        user_id=user_id,
        session=session,
        operation_name="删除产品起名历史记录"
    )


# 产品起名收藏路由已移至 product_favorite_router.py


# ========== 增强的历史查询功能 ==========
@router.get("/history/all", response_model=Dict[str, List])
async def get_all_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    history_type: Optional[str] = Query(None, description="历史类型：name/company/product"),
    user_id: int = Depends(auth_handler.auth_access_dependency),
    session: AsyncSession = Depends(get_session),
):
    """
    获取所有类型的起名历史记录
    支持按类型过滤
    """
    try:
        result = {
            "name_history": [],
            "company_history": [],
            "product_history": []
        }

        # 姓名起名历史
        if history_type is None or history_type == "name":
            name_repo = NameHistoryRepository(session)
            name_histories = await name_repo.get_by_user(user_id, page, page_size)
            result["name_history"] = [history.to_dict() for history in name_histories]

        # 企业起名历史
        if history_type is None or history_type == "company":
            company_repo = CompanyNamingRepository(session)
            company_histories = await company_repo.get_history_by_user(user_id, page, page_size)
            result["company_history"] = [history.to_dict() for history in company_histories]

        # 产品起名历史
        if history_type is None or history_type == "product":
            product_repo = ProductNamingRepository(session)
            product_histories = await product_repo.get_history_by_user(user_id, page, page_size)
            result["product_history"] = [history.to_dict() for history in product_histories]

        return result

    except Exception as e:
        logger.error(f"Failed to get all history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取历史记录失败"
        )

