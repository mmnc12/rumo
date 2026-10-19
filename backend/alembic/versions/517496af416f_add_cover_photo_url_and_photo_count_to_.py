"""add cover_photo_url and photo_count to activities

Revision ID: 517496af416f
Revises: edc0d3c1cbab
Create Date: 2026-10-19 15:13:48.013156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '517496af416f'
down_revision: Union[str, None] = 'edc0d3c1cbab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Adiciona as colunas (com defaults seguros)
    op.add_column(
        "activities",
        sa.Column("cover_photo_url", sa.Text(), nullable=True),
    )
    op.add_column(
        "activities",
        sa.Column(
            "photo_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # 2) Backfill: popula photo_count e cover_photo_url a partir de activity_photos.
    #    cover_photo_url = primeira foto por created_at (mesma regra do photo_service).
    op.execute(
        """
        UPDATE activities a
        SET photo_count = sub.cnt,
            cover_photo_url = sub.cover_url
        FROM (
            SELECT
                activity_id,
                COUNT(*) AS cnt,
                (ARRAY_AGG(url ORDER BY created_at ASC))[1] AS cover_url
            FROM activity_photos
            GROUP BY activity_id
        ) AS sub
        WHERE a.id = sub.activity_id
        """
    )

    # 3) Constraint de sanidade
    op.create_check_constraint(
        "ck_photo_count_non_negative",
        "activities",
        "photo_count >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_photo_count_non_negative", "activities", type_="check"
    )
    op.drop_column("activities", "photo_count")
    op.drop_column("activities", "cover_photo_url")