"""
Database configuration and models for authentication.
Uses SQLAlchemy with PostgreSQL (Neon).
"""
import os
from datetime import datetime
from typing import Optional

try:
    from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("Warning: SQLAlchemy not available. Database features disabled.")

from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Only raise error if auth routes are actually used
# For now, make it optional so chat endpoint works without DB
if not DATABASE_URL:
    print("Warning: DATABASE_URL not found. Authentication features will not work.")
    DATABASE_URL = None

# Create engine only if DATABASE_URL is set and SQLAlchemy is available
if DATABASE_URL and SQLALCHEMY_AVAILABLE:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    except Exception as e:
        print(f"Warning: Could not create database engine: {e}")
        engine = None
        DATABASE_URL = None
else:
    engine = None

# Create session factory only if engine exists
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Base class for models
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = None


if SQLALCHEMY_AVAILABLE and Base:
    class User(Base):
        """
        User model with authentication and personalization fields.
        Compatible with BetterAuth structure.
        """
        __tablename__ = "users"

        id = Column(String, primary_key=True, index=True)  # UUID as string
        email = Column(String, unique=True, index=True, nullable=False)
        name = Column(String, nullable=False)
        password_hash = Column(String, nullable=False)
        
        # Custom fields for personalization (hackathon requirement)
        software_background = Column(Text, nullable=True)  # User's software experience
        hardware_background = Column(Text, nullable=True)   # User's hardware experience
        
        # Standard fields
        email_verified = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
        
        # Additional profile fields
        image = Column(String, nullable=True)  # Profile image URL
        role = Column(String, default="user", nullable=False)  # user, admin, instructor
else:
    # Dummy class if SQLAlchemy not available
    class User:
        pass


def get_db() -> Session:
    """
    Dependency to get database session.
    """
    if not SessionLocal:
        raise RuntimeError("Database not configured. Please set DATABASE_URL in .env")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Run this once to create tables.
    """
    if not SQLALCHEMY_AVAILABLE or not Base or not engine:
        print("Error: Database not configured. Cannot initialize tables.")
        return
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

