"""remove thumbnail field from file model

Revision ID: 7ec38c77ebb0
Revises: 89bf1e74dae5
Create Date: 2025-08-05 03:58:43.690341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ec38c77ebb0"
down_revision: Union[str, None] = "89bf1e74dae5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("files", "thumbnail")


def downgrade() -> None:
    op.add_column("files", sa.Column("thumbnail", sa.String(), nullable=True))
