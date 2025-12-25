import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError

# Import your settings to avoid hardcoding secrets
try:
    from app.core.config import settings
    SECRET_KEY = settings.SECRET_KEY
except ImportError:
    # Fallback if config is missing (Safety net)
    SECRET_KEY = "UNSAFE_DEFAULT_KEY_PLEASE_CHANGE_IN_ENV"

# --- CONFIGURATION ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 Hours

# --- DATABASE SETUP (SQLite Local) ---
# In a real team, this URL would also come from settings
DATABASE_URL = "sqlite:///./users.db"
Base = declarative_base()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- DATA MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)

# Create Tables automatically if they don't exist
Base.metadata.create_all(bind=engine)

# --- SECURITY TOOLS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("AuthService")

class AuthService:
    """
    Handles Identity, Hashing, and Tokens.
    Strictly logic. No HTTP code here.
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
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None