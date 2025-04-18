"""returning roles as enums

Revision ID: b105218290ee
Revises: 9997eb287b5c
Create Date: 2025-04-18 12:56:16.512175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b105218290ee"
down_revision: Union[str, None] = "9997eb287b5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE role AS ENUM ('BASIC', 'SUBSCRIBER', 'ADMIN')")
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("BASIC", "SUBSCRIBER", "ADMIN", name="role"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    op.execute("DROP TYPE role")
