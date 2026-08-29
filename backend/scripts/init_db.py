"""Database initialization and migration utilities"""
from sqlalchemy import text
from app.database import engine, Base
from app.models import *  # Import all models
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def seed_db():
    """Seed database with initial data"""
    try:
        with engine.connect() as connection:
            # Run seed SQL from init.sql
            with open('scripts/init.sql', 'r') as f:
                sql = f.read()
                connection.execute(text(sql))
                connection.commit()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise

if __name__ == "__main__":
    init_db()
    seed_db()
