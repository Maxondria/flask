"""add age column to test migrations

Revision ID: d00eb8cbfc91
Revises: b4df73dfdb84
Create Date: 2020-01-20 12:53:41.049656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd00eb8cbfc91'
down_revision = 'b4df73dfdb84'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('age', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'age')
    # ### end Alembic commands ###
