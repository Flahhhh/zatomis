
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'mysql+pymysql://************@localhost/services?unix_socket=/run/mysqld/mysqld.sock'

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=30,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
