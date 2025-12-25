from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService, SessionLocal

router = APIRouter()
auth_service = AuthService()

# This tells Swagger UI where to find the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- SCHEMAS ---
class UserSignup(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_name: str

# --- DEPENDENCY ---
def get_db():
    """Opens a fresh database connection for the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    db_user = auth_service.create_user(db, user.email, user.password, user.full_name)
    if not db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "Account created successfully"}

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Verifies credentials and issues a JWT Bearer Token.
    """
    user_auth = auth_service.authenticate_user(db, user.email, user.password)
    if not user_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    token = auth_service.create_access_token(data={"sub": user_auth.email, "name": user_auth.full_name})
    
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user_name": user_auth.full_name
    }