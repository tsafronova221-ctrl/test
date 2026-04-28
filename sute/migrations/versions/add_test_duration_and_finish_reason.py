"""add test duration and finish reason

Revision ID: add_test_features
Revises: bd18b4e571c6
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_test_features'
down_revision = 'bd18b4e571c6'
branch_labels = None
depends_on = None


def upgrade():
    # Add test_duration_minutes to labs table
    op.add_column('labs', sa.Column('test_duration_minutes', sa.Integer(), nullable=True, default=0))
    
    # Add finish_reason to attempts table
    op.add_column('attempts', sa.Column('finish_reason', sa.String(length=64), nullable=True, default='completed'))


def downgrade():
    op.drop_column('attempts', 'finish_reason')
    op.drop_column('labs', 'test_duration_minutes')
