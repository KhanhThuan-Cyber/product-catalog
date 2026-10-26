"""rename_create_at_to_created_at

Revision ID: ae62f5c9b050
Revises: 1cd68ac25825
Create Date: 2026-10-26 10:22:12.343089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ae62f5c9b050'
down_revision: Union[str, Sequence[str], None] = '1cd68ac25825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename products.create_at → products.created_at (typo fix)."""
    op.alter_column('products', 'create_at', new_column_name='created_at')


def downgrade() -> None:
    """Rename products.created_at → products.create_at (revert typo fix)."""
    op.alter_column('products', 'created_at', new_column_name='create_at')
