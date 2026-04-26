from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import time


def get_engine():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
            )
            engine.connect()
            print("✅ Database connected successfully")
            return engine
        except Exception as e:
            print(f"Database connection failed. Retrying... ({retries} attempts left)")
            retries -= 1
            time.sleep(5)
    raise Exception("Could not connect to database")


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
