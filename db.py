import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise RuntimeError("DATABASE_URI is required")

engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=1800,
)


