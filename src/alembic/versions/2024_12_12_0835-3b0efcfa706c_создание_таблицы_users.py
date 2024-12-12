"""Создание таблицы users

Revision ID: 3b0efcfa706c
Revises: 
Create Date: 2024-12-12 08:35:25.891037

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b0efcfa706c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("password", sa.LargeBinary(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("id", name=op.f("uq_users_id")),
        sa.UniqueConstraint("login", name=op.f("uq_users_login")),
    )


def downgrade() -> None:
    op.drop_table("users")
