"""empty message

Revision ID: 79658a0b9b61
Revises: 115fe88ba6e0
Create Date: 2021-06-22 09:38:10.970666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79658a0b9b61'
down_revision = '115fe88ba6e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stocks',
    sa.Column('ticker', sa.String(length=5), nullable=False),
    sa.PrimaryKeyConstraint('ticker')
    )
    op.create_table('users_to_stocks',
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.Column('stocks_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stocks_id'], ['stocks.ticker'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_to_stocks')
    op.drop_table('stocks')
    # ### end Alembic commands ###
