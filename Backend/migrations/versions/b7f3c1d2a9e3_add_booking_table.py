"""Add Booking table and link Ticket.booking_id

Revision ID: b7f3c1d2a9e3
Revises: 2b57d8cefde0
Create Date: 2025-12-12 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f3c1d2a9e3'
down_revision = '2b57d8cefde0'
branch_labels = None
depends_on = None


def upgrade():
    # Create booking table
    op.create_table(
        'booking',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('show_id', sa.Integer(), nullable=False),
        sa.Column('reservation_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='reserved'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['show_id'], ['show.id'], ),
        sa.UniqueConstraint('idempotency_key')
    )

    # Add booking_id column to ticket
    with op.batch_alter_table('ticket') as batch_op:
        batch_op.add_column(sa.Column('booking_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_ticket_booking', 'booking', ['booking_id'], ['id'])


def downgrade():
    # Remove booking_id column
    with op.batch_alter_table('ticket') as batch_op:
        batch_op.drop_constraint('fk_ticket_booking', type_='foreignkey')
        batch_op.drop_column('booking_id')

    # Drop booking table
    op.drop_table('booking')
