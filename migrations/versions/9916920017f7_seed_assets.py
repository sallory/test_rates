"""seed assets

Revision ID: 9916920017f7
Revises: 071a1771db5d
Create Date: 2025-09-15 05:56:14.902942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9916920017f7'
down_revision: Union[str, Sequence[str], None] = '071a1771db5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    assets_table = sa.table(
        "assets",
        sa.column("id", sa.Integer),
        sa.column("symbol", sa.String),
    )

    op.bulk_insert(
        assets_table,
        [
            {"id": 1, "symbol": "EURUSD"},
            {"id": 2, "symbol": "USDJPY"},
            {"id": 3, "symbol": "GBPUSD"},
            {"id": 4, "symbol": "AUDUSD"},
            {"id": 5, "symbol": "USDCAD"},
        ],
    )

    op.execute("SELECT setval('assets_id_seq', (SELECT MAX(id) FROM assets))")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM assets WHERE id IN (1,2,3,4,5)")
