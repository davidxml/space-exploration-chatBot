import logging
import os
from datetime import datetime, timedelta, timezone 
from typing import Optional

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError

# --- CONFIGURATION ---
# We use os.getenv directly here. This bypasses the 'Settings' error completely.
# It looks for a system env variable, or falls back to the hardcoded dev key.
SECRET_KEY = os.getenv("SECRET_KEY", "ROYCE_MVP_SECRET_KEY_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./users.db"
Base = declarative_base()

# Connect args needed for SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- USER MODEL ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)

# Create Tables
Base.metadata.create_all(bind=engine)

# --- SECURITY TOOLS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("AuthService")

class AuthService:
    """
    Handles Identity, Hashing, and Tokens.
    """
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, db: Session, email: str, password: str, full_name: str):
        # 1. Check if email exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return None
            
        # 2. Hash Password & Save
        hashed_pw = self.get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed_pw, full_name=full_name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def authenticate_user(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        
        # FIX: Explicitly cast to string to silence Pylance/Pylint errors.
        # This tells the editor "Trust me, this is a string at runtime."
        stored_hash = str(user.hashed_password)
        
        if not self.verify_password(password, stored_hash):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        # Use timezone-aware UTC
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None