"""Database engine, session factory and declarative Base (SQLAlchemy).

The same code serves MySQL, MSSQL and SQLite; only DATABASE_URL changes.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLite only allows a connection to be used by the thread that created it;
# FastAPI serves requests from a thread pool, so that check is disabled for SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pyodbc sends bulk inserts row by row unless fast_executemany is on (MSSQL only).
engine_options = {"fast_executemany": True} if DATABASE_URL.startswith("mssql") else {}

# The engine owns the connection pool. pool_pre_ping drops dead connections
# (e.g. after MySQL's wait_timeout) instead of failing the next request.
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True, **engine_options)

# Each request gets its own Session from this factory (see app/dependencies.py).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from Base; Base.metadata is what Alembic compares against.
Base = declarative_base()
