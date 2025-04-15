"""remove roles

Revision ID: 895e36f6e10c
Revises: b26baf4c5fc3
Create Date: 2025-04-12 13:08:55.204578

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "895e36f6e10c"
down_revision: Union[str, None] = "b26baf4c5fc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "birth_date")
    op.drop_table("roles")


def downgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "system_role", sa.BOOLEAN(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
        sa.UniqueConstraint("id", name="uq_roles_id"),
        sa.UniqueConstraint("title", name="uq_roles_title"),
        postgresql_ignore_search_path=False,
    )
    op.add_column(
        "users",
        sa.Column("birth_date", sa.DATE(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "first_name", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_name", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column("role_id", sa.UUID(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "fk_users_role_id_roles",
        "users",
        "roles",
        ["role_id"],
        ["id"],
        ondelete="SET NULL",
    )

