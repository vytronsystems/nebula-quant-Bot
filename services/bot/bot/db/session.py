from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs.settings import DB_DSN

engine = create_engine(DB_DSN, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
