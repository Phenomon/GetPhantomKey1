#!/usr/bin/env python3
import random
import string
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta

# Configuration: Key expiry time in minutes
KEY_EXPIRY_MINUTES = 5

# Database setup
Base = declarative_base()

class RandomString(Base):
    __tablename__ = 'random_strings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), nullable=False, unique=True)
    string_value = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_random_string(length=20):
    """Generate a random alphanumeric string of specified length"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def save_string_to_db(user_id, string_value):
    """Save the generated string to the database with user ID"""
    session = SessionLocal()
    try:
        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(minutes=KEY_EXPIRY_MINUTES)
        
        # Check if user already has a key
        existing_key = session.query(RandomString).filter_by(user_id=user_id).first()
        
        if existing_key:
            # Delete existing key and create new one
            session.delete(existing_key)
            session.flush()
        
        # Create new key
        new_string = RandomString(
            user_id=user_id, 
            string_value=string_value,
            expires_at=expires_at
        )
        session.add(new_string)
        session.commit()
        return new_string.id
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    finally:
        session.close()

def get_existing_key(user_id):
    """Get the existing key from the database for a specific user if not expired"""
    session = SessionLocal()
    try:
        current_time = datetime.utcnow()
        
        # Query for non-expired key
        existing_string = session.query(RandomString).filter(
            RandomString.user_id == user_id,
            RandomString.expires_at > current_time
        ).first()
        
        if existing_string is not None:
            return existing_string.string_value
        else:
            # Clean up any expired keys for this user
            expired_keys = session.query(RandomString).filter(
                RandomString.user_id == user_id,
                RandomString.expires_at <= current_time
            ).all()
            
            for expired_key in expired_keys:
                session.delete(expired_key)
            
            if expired_keys:
                session.commit()
            
            return None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        session.close()

def get_or_create_key(user_id):
    """Get existing key or create a new one for a specific user"""
    # Check if we already have a valid key for this user
    existing_key = get_existing_key(user_id)
    
    if existing_key is not None:
        return existing_key
    else:
        # Generate new key and save it
        new_key = generate_random_string(20)
        save_result = save_string_to_db(user_id, new_key)
        
        if save_result is not None:
            return new_key
        else:
            return None

def generate_user_id():
    """Generate a unique user ID"""
    return str(random.randint(100000, 999999))

if __name__ == "__main__":
    # Test the functions
    test_user_id = generate_user_id()
    print(f"Generated user ID: {test_user_id}")
    
    key = get_or_create_key(test_user_id)
    print(f"Generated key: {key}")
