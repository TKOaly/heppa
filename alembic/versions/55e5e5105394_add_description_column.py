"""add description column

Revision ID: 55e5e5105394
Revises: 
Create Date: 2024-05-24 23:07:13.395695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55e5e5105394'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('candidate', sa.Column('description', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('candidate', 'description')
