"""change owner id to owner uid

Revision ID: 9e268d8b8440
Revises: f6b26d01fe0a
Create Date: 2020-12-21 14:21:14.128550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e268d8b8440'
down_revision = 'f6b26d01fe0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('study', sa.Column('owner_uid', sa.Integer(), nullable=False))
    op.drop_constraint('study_owner_id_fkey', 'study', type_='foreignkey')
    op.create_foreign_key(None, 'study', 'user', ['owner_uid'], ['uid'], ondelete='CASCADE')
    op.drop_column('study', 'owner_id')
    op.add_column('task', sa.Column('owner_uid', sa.Integer(), nullable=False))
    op.drop_constraint('task_owner_id_fkey', 'task', type_='foreignkey')
    op.create_foreign_key(None, 'task', 'user', ['owner_uid'], ['uid'], ondelete='CASCADE')
    op.drop_column('task', 'owner_id')
    op.add_column('trade', sa.Column('owner_uid', sa.Integer(), nullable=False))
    op.drop_constraint('trade_owner_id_fkey', 'trade', type_='foreignkey')
    op.create_foreign_key(None, 'trade', 'user', ['owner_uid'], ['uid'], ondelete='CASCADE')
    op.drop_column('trade', 'owner_id')
    op.add_column('tradingplan', sa.Column('owner_uid', sa.Integer(), nullable=False))
    op.drop_constraint('tradingplan_owner_id_fkey', 'tradingplan', type_='foreignkey')
    op.create_foreign_key(None, 'tradingplan', 'user', ['owner_uid'], ['uid'], ondelete='CASCADE')
    op.drop_column('tradingplan', 'owner_id')
    op.add_column('watchlist', sa.Column('owner_uid', sa.Integer(), nullable=False))
    op.drop_constraint('watchlist_owner_id_fkey', 'watchlist', type_='foreignkey')
    op.create_foreign_key(None, 'watchlist', 'user', ['owner_uid'], ['uid'], ondelete='CASCADE')
    op.drop_column('watchlist', 'owner_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('watchlist', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'watchlist', type_='foreignkey')
    op.create_foreign_key('watchlist_owner_id_fkey', 'watchlist', 'user', ['owner_id'], ['uid'], ondelete='CASCADE')
    op.drop_column('watchlist', 'owner_uid')
    op.add_column('tradingplan', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'tradingplan', type_='foreignkey')
    op.create_foreign_key('tradingplan_owner_id_fkey', 'tradingplan', 'user', ['owner_id'], ['uid'], ondelete='CASCADE')
    op.drop_column('tradingplan', 'owner_uid')
    op.add_column('trade', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'trade', type_='foreignkey')
    op.create_foreign_key('trade_owner_id_fkey', 'trade', 'user', ['owner_id'], ['uid'], ondelete='CASCADE')
    op.drop_column('trade', 'owner_uid')
    op.add_column('task', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.create_foreign_key('task_owner_id_fkey', 'task', 'user', ['owner_id'], ['uid'], ondelete='CASCADE')
    op.drop_column('task', 'owner_uid')
    op.add_column('study', sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'study', type_='foreignkey')
    op.create_foreign_key('study_owner_id_fkey', 'study', 'user', ['owner_id'], ['uid'], ondelete='CASCADE')
    op.drop_column('study', 'owner_uid')
    # ### end Alembic commands ###
