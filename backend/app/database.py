import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Defaults to a local SQLite file for zero-config demo/dev runs.
# For the production/target stack, set DATABASE_URL to a Postgres DSN, e.g.
#   postgresql+psycopg2://user:password@localhost:5432/packaging_ai
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./packaging_ai.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
