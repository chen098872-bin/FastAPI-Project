"""add company_name_history product_name_history table

Revision ID: 44c670a17ff0
Revises: d68861c80fc6
Create Date: 2025-12-27 15:22:07.788709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44c670a17ff0'
down_revision: Union[str, Sequence[str], None] = 'd68861c80fc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add company and product naming tables"""

    # Create company_name_history table
    op.create_table('company_name_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=False),
        sa.Column('company_type', sa.String(length=50), nullable=False),
        sa.Column('business_scope', sa.Text(), nullable=False),
        sa.Column('positioning', sa.String(length=200), nullable=True),
        sa.Column('length', sa.String(length=20), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=True),
        sa.Column('exclude', sa.JSON(), nullable=False),
        sa.Column('generated_names', sa.JSON(), nullable=False),
        sa.Column('model_used', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create company_name_favorite table
    op.create_table('company_name_favorite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['history_id'], ['company_name_history.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_name_history table
    op.create_table('product_name_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_type', sa.String(length=100), nullable=False),
        sa.Column('product_function', sa.Text(), nullable=False),
        sa.Column('target_audience', sa.String(length=200), nullable=True),
        sa.Column('market_positioning', sa.String(length=200), nullable=True),
        sa.Column('length', sa.String(length=20), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=True),
        sa.Column('exclude', sa.JSON(), nullable=False),
        sa.Column('generated_names', sa.JSON(), nullable=False),
        sa.Column('model_used', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_name_favorite table
    op.create_table('product_name_favorite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['history_id'], ['product_name_history.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index(op.f('ix_company_name_history_user_id'), 'company_name_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_company_name_history_created_at'), 'company_name_history', ['created_at'], unique=False)
    op.create_index(op.f('ix_company_name_favorite_user_id'), 'company_name_favorite', ['user_id'], unique=False)
    op.create_index(op.f('ix_product_name_history_user_id'), 'product_name_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_product_name_history_created_at'), 'product_name_history', ['created_at'], unique=False)
    op.create_index(op.f('ix_product_name_favorite_user_id'), 'product_name_favorite', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: remove company and product naming tables"""

    # Drop indexes
    op.drop_index(op.f('ix_product_name_favorite_user_id'), table_name='product_name_favorite')
    op.drop_index(op.f('ix_product_name_history_created_at'), table_name='product_name_history')
    op.drop_index(op.f('ix_product_name_history_user_id'), table_name='product_name_history')
    op.drop_index(op.f('ix_company_name_favorite_user_id'), table_name='company_name_favorite')
    op.drop_index(op.f('ix_company_name_history_created_at'), table_name='company_name_history')
    op.drop_index(op.f('ix_company_name_history_user_id'), table_name='company_name_history')

    # Drop tables
    op.drop_table('product_name_favorite')
    op.drop_table('product_name_history')
    op.drop_table('company_name_favorite')
    op.drop_table('company_name_history')
