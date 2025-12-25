import logging
import time
from typing import List, Any, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

# LangChain Imports
from langchain_core.messages import HumanMessage, AIMessage

# Internal Services
from app.services.vector_db import VectorDBService
from app.services.llm_engine import SpaceBrain
from app.services.auth_service import AuthService, SessionLocal

# --- SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Royce-Backend")

auth_service = AuthService()
# This tells Swagger UI where to find the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- GLOBAL STATE ---
# We tell Python: "This dictionary keys are strings, but the values can be ANY object."
system_state: Dict[str, Any] = {
    "brain": None,
    "vector_store": None
}

# --- DATA MODELS ---
class UserSignup(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    latency: float

# --- DEPENDENCIES ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# THE GATEKEEPER: Verifies Token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"] # Returns email

# --- LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 STARTUP: SECURING DATA CHANNELS...")
    try:
        vdb = VectorDBService()
        system_state["vector_store"] = vdb.load_knowledge_base()
        system_state["brain"] = SpaceBrain()
        logger.info("✅ SYSTEMS ONLINE.")
    except Exception as e:
        logger.error(f"❌ STARTUP ERROR: {e}")
    yield
    system_state.clear()

app = FastAPI(title="Royce Secure Backend", lifespan=lifespan)

# --- AUTH ENDPOINTS ---
@app.post("/auth/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    db_user = auth_service.create_user(db, user.email, user.password, user.full_name)
    if not db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "Account created successfully"}

@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_auth = auth_service.authenticate_user(db, user.email, user.password)
    if not user_auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_service.create_access_token(data={"sub": user_auth.email, "name": user_auth.full_name})
    return {"access_token": token, "token_type": "bearer", "user_name": user_auth.full_name}

# --- PROTECTED CHAT ENDPOINT ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: str = Depends(get_current_user)):
    start_time = time.time()
    
    if not system_state["brain"]:
        raise HTTPException(status_code=503, detail="System initializing...")

    # Reconstruct History
    lc_history = []
    for msg in request.history:
        role_obj = HumanMessage if msg.role == "user" else AIMessage
        lc_history.append(role_obj(content=msg.content))
    
    # RAG Retrieval
    try:
        results = system_state["vector_store"].similarity_search(request.message, k=3)
        context_chunks = [doc.page_content for doc in results]
    except:
        context_chunks = []
        results = []

    # Generate
    try:
        ai_reply = system_state["brain"].chat(request.message, context_chunks, lc_history)
    except Exception as e:
        logger.error(f"Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Neural Core Error")

    return ChatResponse(
        response=ai_reply,
        sources=[doc.metadata.get("source", "unknown") for doc in results],
        latency=round(time.time() - start_time, 2)
    )