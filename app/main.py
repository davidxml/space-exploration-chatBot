import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Internal Modules
from app.core.config import settings
from app.api.routes import router as api_router
from app.services.llm_engine import SpaceBrain
from app.services.vector_db import VectorDBService

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Royce-System")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    STARTUP: Loads the heavy AI models into RAM.
    SHUTDOWN: Cleans up resources.
    """
    logger.info("🚀 SYSTEM BOOT SEQUENCE INITIATED...")
    
    # 1. Load Vector Database
    try:
        vdb = VectorDBService()
        # Explicitly load the knowledge base into memory
        vdb.load_knowledge_base() 
        # Store the SERVICE instance itself in the app state
        app.state.vector_store = vdb 
        
        logger.info("✅ Knowledge Base Online.")
    except Exception as e:
        logger.error(f"❌ Vector DB Failure: {e}")
        app.state.vector_store = None

    # 2. Load Neural Core (LLM)
    try:
        app.state.brain = SpaceBrain()
        logger.info("✅ Neural Core (Llama 3.3) Online.")
    except Exception as e:
        logger.error(f"❌ LLM Connection Failure: {e}")
        app.state.brain = None

    yield # Application Runs Here...

    # Shutdown
    logger.info("💤 System Shutdown.")
    app.state.vector_store = None
    app.state.brain = None

# Initialize App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS (Allow Frontend to talk to Backend)
# In production, replace ["*"] with specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the "Traffic Controller" (Routes)
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- DIRECT EXECUTION ENTRY POINT ---
if __name__ == "__main__":
    import uvicorn
    # This allows you to run 'python app/main.py' directly
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)