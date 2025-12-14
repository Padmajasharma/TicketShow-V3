"""add movie, screen and offer tables; add screen_id/movie_id to show and ticket

Revision ID: c4b1e9d8f0e2
Revises: a5e9eb0d513f
Create Date: 2025-12-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4b1e9d8f0e2'
down_revision = 'a5e9eb0d513f'
branch_labels = None
depends_on = None


def upgrade():
    # Create movie table
    op.create_table(
        'movie',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('tmdb_id', sa.Integer(), nullable=True),
        sa.Column('overview', sa.Text(), nullable=True),
        sa.Column('runtime', sa.Integer(), nullable=True),
        sa.Column('release_date', sa.String(length=20), nullable=True),
        sa.Column('tmdb_rating', sa.Float(), nullable=True),
        sa.Column('backdrop', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_movie_title', 'movie', ['title'])
    op.create_index('ix_movie_tmdb_id', 'movie', ['tmdb_id'])

    # Create screen table
    op.create_table(
        'screen',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('theatre_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False, default=0),
        sa.ForeignKeyConstraint(['theatre_id'], ['theatre.id']),
    )

    # Create offer table
    op.create_table(
        'offer',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('discount_type', sa.String(length=20), nullable=False, server_default='percent'),
        sa.Column('discount_value', sa.Float(), nullable=False, server_default='0'),
        sa.Column('show_id', sa.Integer(), nullable=True),
        sa.Column('theatre_id', sa.Integer(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, server_default=sa.sql.expression.true()),
        sa.Column('starts_at', sa.DateTime(), nullable=True),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['show_id'], ['show.id']),
        sa.ForeignKeyConstraint(['theatre_id'], ['theatre.id']),
        sa.UniqueConstraint('code', name='uq_offer_code'),
    )

    # Add movie_id and screen_id to show
    with op.batch_alter_table('show') as batch_op:
        batch_op.add_column(sa.Column('screen_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('movie_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_show_screen', 'screen', ['screen_id'], ['id'])
        batch_op.create_foreign_key('fk_show_movie', 'movie', ['movie_id'], ['id'])
        batch_op.create_index('ix_show_start_time', ['start_time'])

    # Add screen_id and booked_at to ticket (ensure booked_at exists before index)
    with op.batch_alter_table('ticket') as batch_op:
        batch_op.add_column(sa.Column('screen_id', sa.Integer(), nullable=True))
        # Add booked_at column if it does not exist (for fresh DBs)
        try:
            batch_op.add_column(sa.Column('booked_at', sa.DateTime(), nullable=True))
        except Exception:
            pass
        batch_op.create_foreign_key('fk_ticket_screen', 'screen', ['screen_id'], ['id'])
        batch_op.create_index('ix_ticket_show_id', ['show_id'])
        batch_op.create_index('ix_ticket_booked_at', ['booked_at'])

    # Add screen_id to theatre_seat and change unique constraint
    with op.batch_alter_table('theatre_seat') as batch_op:
        # drop old unique constraint if present
        try:
            batch_op.drop_constraint('unique_theatre_seat', type_='unique')
        except Exception:
            pass
        batch_op.add_column(sa.Column('screen_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_theatre_seat_screen', 'screen', ['screen_id'], ['id'])
        batch_op.create_unique_constraint('unique_screen_seat', ['screen_id', 'row_label', 'seat_number'])


def downgrade():
    # reverse changes
    with op.batch_alter_table('theatre_seat') as batch_op:
        batch_op.drop_constraint('unique_screen_seat', type_='unique')
        try:
            batch_op.drop_constraint('fk_theatre_seat_screen', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_column('screen_id')
        except Exception:
            pass
        # re-create old unique constraint
        try:
            batch_op.create_unique_constraint('unique_theatre_seat', ['theatre_id', 'row_label', 'seat_number'])
        except Exception:
            pass

    with op.batch_alter_table('ticket') as batch_op:
        try:
            batch_op.drop_index('ix_ticket_booked_at')
        except Exception:
            pass
        try:
            batch_op.drop_index('ix_ticket_show_id')
        except Exception:
            pass
        try:
            batch_op.drop_constraint('fk_ticket_screen', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_column('screen_id')
        except Exception:
            pass

    with op.batch_alter_table('show') as batch_op:
        try:
            batch_op.drop_index('ix_show_start_time')
        except Exception:
            pass
        try:
            batch_op.drop_constraint('fk_show_movie', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_constraint('fk_show_screen', type_='foreignkey')
        except Exception:
            pass
        try:
            batch_op.drop_column('movie_id')
        except Exception:
            pass
        try:
            batch_op.drop_column('screen_id')
        except Exception:
            pass

    op.drop_table('offer')
    op.drop_table('screen')
    op.drop_index('ix_movie_tmdb_id', table_name='movie')
    op.drop_index('ix_movie_title', table_name='movie')
    op.drop_table('movie')
