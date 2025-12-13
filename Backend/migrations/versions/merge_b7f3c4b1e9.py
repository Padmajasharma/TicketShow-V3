"""merge heads b7f3c1d2a9e3 and c4b1e9d8f0e2

Revision ID: merge_b7f3c4b1e9
Revises: b7f3c1d2a9e3, c4b1e9d8f0e2
Create Date: 2025-12-12 12:10:00.000000

This is an empty merge revision to join the two migration branches.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_b7f3c4b1e9'
down_revision = ('b7f3c1d2a9e3', 'c4b1e9d8f0e2')
branch_labels = None
depends_on = None


def upgrade():
    # merge-only revision; no schema changes
    pass


def downgrade():
    # nothing to undo
    pass
