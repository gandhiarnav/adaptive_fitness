"""add_saved_meals_and_manual_journal_columns

Revision ID: a1b2c3d4e5f6
Revises: 66a9048092d9
Create Date: 2026-08-01 14:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '66a9048092d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
        {"t": table_name},
    )
    return result.fetchone() is not None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(sa.text(f"PRAGMA table_info({table_name})"))
    return any(row[1] == column_name for row in result.fetchall())


def upgrade() -> None:
    """
    1. Create saved_meals table (skip if it already exists).
    2. Add is_manual column to food_journal.
    3. Migrate estimated_calories / estimated_protein from Integer → Float
       (batch mode for SQLite compatibility).
    """
    conn = op.get_bind()

    # ── 1. saved_meals ────────────────────────────────────────────────────────
    if not _table_exists(conn, 'saved_meals'):
        op.create_table(
            'saved_meals',
            sa.Column('id',         sa.Integer(),  primary_key=True),
            sa.Column('user_id',    sa.Integer(),  sa.ForeignKey('users.id'), nullable=False),
            sa.Column('name',       sa.String(),   nullable=False),
            sa.Column('calories',   sa.Float(),    nullable=False),
            sa.Column('protein',    sa.Float(),    nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        )
        op.create_index('ix_saved_meals_id', 'saved_meals', ['id'], unique=False)

    # ── 2 & 3. food_journal alterations ──────────────────────────────────────
    with op.batch_alter_table('food_journal') as batch_op:
        # Add is_manual flag (default FALSE for existing rows).
        # Only add if not already there (idempotent).
        if not _column_exists(conn, 'food_journal', 'is_manual'):
            batch_op.add_column(
                sa.Column('is_manual', sa.Boolean(), nullable=False, server_default=sa.false())
            )
        # Upgrade estimated_* to Float so decimals are preserved.
        batch_op.alter_column(
            'estimated_calories',
            existing_type=sa.Integer(),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            'estimated_protein',
            existing_type=sa.Integer(),
            type_=sa.Float(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Reverse all changes."""
    with op.batch_alter_table('food_journal') as batch_op:
        batch_op.alter_column(
            'estimated_protein',
            existing_type=sa.Float(),
            type_=sa.Integer(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            'estimated_calories',
            existing_type=sa.Float(),
            type_=sa.Integer(),
            existing_nullable=True,
        )
        batch_op.drop_column('is_manual')

    op.drop_index('ix_saved_meals_id', table_name='saved_meals')
    op.drop_table('saved_meals')
