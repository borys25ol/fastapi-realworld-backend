"""add article versions

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-03-21 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'xxxx'
down_revision: Union[str, None] = 'previous_revision'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add new columns to article table
    op.add_column('article', sa.Column('is_draft', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('article', sa.Column('current_version', sa.Integer(), nullable=False, server_default='1'))

    # Create article_versions table
    op.create_table(
        'article_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('body', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['article_id'], ['article.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_article_versions_article_id', 'article_versions', ['article_id'])

def downgrade() -> None:
    op.drop_index('ix_article_versions_article_id')
    op.drop_table('article_versions')
    op.drop_column('article', 'current_version')
    op.drop_column('article', 'is_draft') 