from alembic import op
import sqlalchemy as sa

revision = "0001_create_subscribers_table"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute(
        """
    CREATE TABLE IF NOT EXISTS subscribers (
      id BIGSERIAL PRIMARY KEY,
      email TEXT NOT NULL,
      email_norm TEXT GENERATED ALWAYS AS (lower(trim(email))) STORED,
      source TEXT,
      user_agent TEXT,
      job_id TEXT,
      subscribed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      unsubscribed_at TIMESTAMPTZ
    );
    """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_subscribers_email_norm ON subscribers(email_norm);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_subscribers_subscribed_at ON subscribers(subscribed_at DESC);"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_subscribers_subscribed_at;")
    op.execute("DROP INDEX IF EXISTS ux_subscribers_email_norm;")
    op.execute("DROP TABLE IF EXISTS subscribers;")


