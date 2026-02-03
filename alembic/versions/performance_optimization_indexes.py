"""performance optimization indexes

Revision ID: perf_opt_001
Revises: 44c670a17ff0
Create Date: 2025-12-27 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'perf_opt_001'
down_revision: Union[str, Sequence[str], None] = '44c670a17ff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance optimization indexes"""

    # 为name_history表添加复合索引 (最常用的查询模式)
    op.create_index(
        'ix_name_history_user_created',
        'name_history',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 为name_history添加model_used索引 (用于统计)
    op.create_index(
        'ix_name_history_model_used',
        'name_history',
        ['model_used'],
        unique=False
    )

    # 为company_name_history添加复合索引
    op.create_index(
        'ix_company_name_history_user_created',
        'company_name_history',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 为company_name_history添加industry索引 (用于按行业筛选)
    op.create_index(
        'ix_company_name_history_industry',
        'company_name_history',
        ['industry'],
        unique=False
    )

    # 为company_name_favorite添加复合索引
    op.create_index(
        'ix_company_name_favorite_user_created',
        'company_name_favorite',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 为product_name_history添加复合索引
    op.create_index(
        'ix_product_name_history_user_created',
        'product_name_history',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 为product_name_history添加product_type索引
    op.create_index(
        'ix_product_name_history_product_type',
        'product_name_history',
        ['product_type'],
        unique=False
    )

    # 为product_name_favorite添加复合索引
    op.create_index(
        'ix_product_name_favorite_user_created',
        'product_name_favorite',
        ['user_id', sa.text('created_at DESC')],
        unique=False
    )

    # 为name_usage添加复合索引 (统计查询优化)
    op.create_index(
        'ix_name_usage_name_gender_region',
        'name_usage',
        ['name', 'gender', 'region'],
        unique=False
    )

    # 为name_usage添加时间索引
    op.create_index(
        'ix_name_usage_recorded_at',
        'name_usage',
        [sa.text('recorded_at DESC')],
        unique=False
    )

    # 为email_code添加复合索引 (邮箱+验证码查询)
    op.create_index(
        'ix_email_code_email_created',
        'email_code',
        ['email', sa.text('create_time DESC')],
        unique=False
    )

    # 为user表的phone添加索引 (如果还没有的话)
    op.create_index(
        'ix_user_phone',
        'user',
        ['phone'],
        unique=False
    )

    # 为user表的nickname添加索引 (用于搜索)
    op.create_index(
        'ix_user_nickname',
        'user',
        ['nickname'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance optimization indexes"""

    # 删除所有添加的索引
    op.drop_index('ix_name_history_user_created', table_name='name_history')
    op.drop_index('ix_name_history_model_used', table_name='name_history')
    op.drop_index('ix_company_name_history_user_created', table_name='company_name_history')
    op.drop_index('ix_company_name_history_industry', table_name='company_name_history')
    op.drop_index('ix_company_name_favorite_user_created', table_name='company_name_favorite')
    op.drop_index('ix_product_name_history_user_created', table_name='product_name_history')
    op.drop_index('ix_product_name_history_product_type', table_name='product_name_history')
    op.drop_index('ix_product_name_favorite_user_created', table_name='product_name_favorite')
    op.drop_index('ix_name_usage_name_gender_region', table_name='name_usage')
    op.drop_index('ix_name_usage_recorded_at', table_name='name_usage')
    op.drop_index('ix_email_code_email_created', table_name='email_code')
    op.drop_index('ix_user_phone', table_name='user')
    op.drop_index('ix_user_nickname', table_name='user')
