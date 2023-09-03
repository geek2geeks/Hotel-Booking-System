"""empty message

Revision ID: eb7507e10d23
Revises: c050e6721c43
Create Date: 2023-09-03 19:21:56.698477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb7507e10d23'
down_revision = 'c050e6721c43'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('reservation')
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=50), nullable=True))

    op.create_table('reservation',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('check_in_date', sa.DATETIME(), nullable=False),
    sa.Column('check_out_date', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('room_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('booking')
    # ### end Alembic commands ###
