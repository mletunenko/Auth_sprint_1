"""системные роли и ограничения удаления

Revision ID: 6cce8b8c000a
Revises: 48ed9c5d8c8c
Create Date: 2024-12-22 02:29:48.190702

"""

from datetime import datetime, timezone
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

from schemas.enums import SystemRoles

import models
from core.config import settings

# revision identifiers, used by Alembic.
revision: str = "6cce8b8c000a"
down_revision: Union[str, None] = "48ed9c5d8c8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Insert predefined roles
    roles_table = sa.table(
        "roles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.Column("title", sa.String),
        sa.Column("system_role", sa.Boolean),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
    )
    created_at = datetime.now(timezone.utc)
    op.bulk_insert(
        roles_table,
        [
            {
                "id": str(uuid4()),
                "title": "superuser",
                "system_role": True,
                "created_at": created_at,
            },
            {"id": str(uuid4()), "title": "admin", "system_role": True, "created_at": created_at},
            {
                "id": str(uuid4()),
                "title": "subscriber",
                "system_role": False,
                "created_at": created_at,
            },
            {
                "id": str(uuid4()),
                "title": "regular user",
                "system_role": False,
                "created_at": created_at,
            },
        ],
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_deletion_of_system_roles()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.system_role THEN
                RAISE EXCEPTION 'Cannot delete system roles';
            END IF;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    """
    )
    op.execute(
        """
        CREATE TRIGGER prevent_system_role_deletion
        BEFORE DELETE ON roles
        FOR EACH ROW
        EXECUTE FUNCTION prevent_deletion_of_system_roles();
    """
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS prevent_system_role_deletion ON roles;")
    op.execute("DROP FUNCTION IF EXISTS prevent_deletion_of_system_roles;")
