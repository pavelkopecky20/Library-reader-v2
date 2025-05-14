from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '075c3964d491'
down_revision = 'e872623c3a6b'
branch_labels = None
depends_on = None

# Check if the dialect is SQLite
def is_sqlite():
    return op.get_bind().dialect.name == "sqlite"

def upgrade():
    if is_sqlite():
        # Workaround for SQLite: recreate the table
        with op.batch_alter_table("book") as batch_op:
            batch_op.alter_column("title", nullable=True)
    else:
        # For other databases, use the standard alter_column
        op.alter_column("book", "title", nullable=True)

def downgrade():
    if is_sqlite():
        # Workaround for SQLite: recreate the table
        with op.batch_alter_table("book") as batch_op:
            batch_op.alter_column("title", nullable=False)
    else:
        # For other databases, use the standard alter_column
        op.alter_column("book", "title", nullable=False)