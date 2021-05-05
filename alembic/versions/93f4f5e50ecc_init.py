"""init

Revision ID: 93f4f5e50ecc
Revises:
Create Date: 2021-05-05 16:17:41.790465

"""
import sqlalchemy as sa

from alembic import op

revision = '93f4f5e50ecc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'taxon',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ancestry', sa.String(), nullable=True),
        sa.Column('rank', sa.String(), nullable=True),
        sa.Column('rank_level', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_taxon_id'), 'taxon', ['id'], unique=False)
    op.create_index(op.f('ix_taxon_name'), 'taxon', ['name'], unique=False)
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_login'), 'user', ['login'], unique=False)
    op.create_table(
        'observation',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('positional_accuracy', sa.Integer(), nullable=True),
        sa.Column('taxon_id', sa.Integer(), nullable=True),
        sa.Column('quality_grade', sa.String(), nullable=True),
        sa.Column('observed_on', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['taxon_id'],
            ['taxon.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_index(
        op.f('ix_observation_observed_on'), 'observation', ['observed_on'], unique=False
    )
    op.create_index(
        op.f('ix_observation_quality_grade'), 'observation', ['quality_grade'], unique=False
    )
    op.create_index(op.f('ix_observation_taxon_id'), 'observation', ['taxon_id'], unique=False)
    op.create_index(op.f('ix_observation_user_id'), 'observation', ['user_id'], unique=False)
    op.create_index(op.f('ix_observation_uuid'), 'observation', ['uuid'], unique=False)
    op.create_table(
        'photo',
        sa.Column('uuid', sa.String(), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=True),
        sa.Column('observation_uuid', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('extension', sa.String(), nullable=True),
        sa.Column('license', sa.String(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['observation_uuid'],
            ['observation.uuid'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('uuid'),
    )
    op.create_index(op.f('ix_photo_observation_uuid'), 'photo', ['observation_uuid'], unique=False)
    op.create_index(op.f('ix_photo_user_id'), 'photo', ['user_id'], unique=False)
    op.create_index(op.f('ix_photo_uuid'), 'photo', ['uuid'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_photo_uuid'), table_name='photo')
    op.drop_index(op.f('ix_photo_user_id'), table_name='photo')
    op.drop_index(op.f('ix_photo_observation_uuid'), table_name='photo')
    op.drop_table('photo')
    op.drop_index(op.f('ix_observation_uuid'), table_name='observation')
    op.drop_index(op.f('ix_observation_user_id'), table_name='observation')
    op.drop_index(op.f('ix_observation_taxon_id'), table_name='observation')
    op.drop_index(op.f('ix_observation_quality_grade'), table_name='observation')
    op.drop_index(op.f('ix_observation_observed_on'), table_name='observation')
    op.drop_table('observation')
    op.drop_index(op.f('ix_user_login'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_taxon_name'), table_name='taxon')
    op.drop_index(op.f('ix_taxon_id'), table_name='taxon')
    op.drop_table('taxon')
