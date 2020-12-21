"""style owner_uid to nullable

Revision ID: f6b26d01fe0a
Revises: 859e8df1f7b9
Create Date: 2020-12-20 13:08:50.590374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6b26d01fe0a'
down_revision = '859e8df1f7b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('style', 'owner_uid',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('style', 'owner_uid',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
