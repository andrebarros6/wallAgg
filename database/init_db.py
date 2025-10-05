from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config.settings import settings
import os

def init_database(db_url: str = None):
    """Initialize database and create tables"""
    if db_url is None:
        db_url = settings.DATABASE_URL

    # Create data directory if using SQLite
    if db_url.startswith('sqlite:'):
        db_path = db_url.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    # Create engine
    engine = create_engine(db_url, echo=settings.DEBUG)

    # Create all tables
    Base.metadata.create_all(engine)

    # Return session maker
    return sessionmaker(bind=engine)

def get_session():
    """Get database session"""
    SessionLocal = init_database()
    return SessionLocal()
