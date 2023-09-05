"""Added status attribute to Booking model

Revision ID: 24f0cae5d080
Revises: 23d26a5b1eef
Create Date: 2023-09-05 19:56:25.780886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24f0cae5d080'
down_revision = '23d26a5b1eef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', name='bookingstatus'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
