"""Add question_candidates table for Jev-ranked candidate pool

Revision ID: 3f9a1c2e4b5d
Revises: ee28b0a06f31
Create Date: 2026-09-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.core.db_types


# revision identifiers, used by Alembic.
revision: str = '3f9a1c2e4b5d'
down_revision: Union[str, None] = 'ee28b0a06f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('question_candidates',
    sa.Column('id', app.core.db_types.GUID(), nullable=False),
    sa.Column('thread_id', app.core.db_types.GUID(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('time_focus', sa.JSON(), nullable=True),
    sa.Column('topic_focus', sa.JSON(), nullable=True),
    sa.Column('move', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('jev_probability', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('presented_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['thread_id'], ['threads.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_question_candidates_thread_status'),
        'question_candidates', ['thread_id', 'status'], unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_question_candidates_thread_status'),
                  table_name='question_candidates')
    op.drop_table('question_candidates')
