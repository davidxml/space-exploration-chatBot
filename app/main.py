import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Routers
from app.api import auth, routes

# Import Services
from app.services.vector_db import VectorDBService
from app.services.llm_engine import SpaceBrain
from app.core.config import settings

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Royce-Backend")

# --- LIFECYCLE MANAGER (The On/Off Switch) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 SYSTEM STARTUP: INITIALIZING CORTEX...")
    try:
        # 1. Initialize Memory (Vector DB)
        vdb = VectorDBService()
        
        # FIX: Load the index internally, but do not assign the result to app.state
        vdb.load_knowledge_base() 
        
        # FIX: Store the SERVICE OBJECT, not the raw index.
        # This ensures routes can call vdb.search()
        app.state.vector_store = vdb
        
        # 2. Initialize Brain (LLM)
        app.state.brain = SpaceBrain()
        
        logger.info("✅ ROYCE ONLINE. SYSTEMS NOMINAL.")
    except Exception as e:
        logger.critical(f"❌ STARTUP FAILED: {e}")
        # In production, we don't want to crash, but we should warn heavily
    
    yield
    
    # Cleanup
    logger.info("💤 SHUTDOWN: CLEARING MEMORY...")
    app.state.vector_store = None
    app.state.brain = None

# --- APP DEFINITION ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# --- SECURITY: CORS ---
# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your Streamlit URL in strict production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION (The Wiring) ---
app.include_router(auth.router, prefix="/auth", tags=["Security"])
app.include_router(routes.router, tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Royce Neural Core is Active"}