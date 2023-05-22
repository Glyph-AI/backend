from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)