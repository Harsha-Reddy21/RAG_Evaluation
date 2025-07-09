from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
from models import Base
from config import DATABASE_URL

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    """Database connection manager for the financial RAG system"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = None
        self.SessionLocal = None
        self.db_url = db_url
    
    def connect(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(self.db_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            logger.info("Database connection established and tables created")
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        if not self.SessionLocal:
            self.connect()
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

# Create a database instance
db = Database()

# Dependency to get DB session
def get_db():
    """Dependency for FastAPI to get a database session"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close() 