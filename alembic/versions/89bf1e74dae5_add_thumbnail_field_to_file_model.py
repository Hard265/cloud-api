"""add thumbnail field to file model

Revision ID: 89bf1e74dae5
Revises: 392805ee004d
Create Date: 2025-08-05 03:42:20.731924

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "89bf1e74dae5"
down_revision: Union[str, None] = "392805ee004d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("files", sa.Column("thumbnail", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("files", "thumbnail")
