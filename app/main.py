import logging
import time
from typing import List, Dict, Any
from contextlib import asynccontextmanager

# FastAPI Framework
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# LangChain types for memory reconstruction
from langchain_core.messages import HumanMessage, AIMessage

# --- INTERNAL MODULES ---
# These are the files we built earlier.
from app.services.vector_db import VectorDBService
from app.services.llm_engine import SpaceBrain

# --- 1. LOGGING SETUP ---
# This ensures we see errors in the terminal when running the server.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Royce-Backend")

# --- 2. GLOBAL STATE STORE ---
# This dictionary acts as the server's "RAM". 
# It holds the heavy AI models so they stay loaded in memory.
system_state = {
    "brain": None,       # Will hold the SpaceBrain (Llama 3.3) instance
    "vector_store": None # Will hold the FAISS Knowledge Base
}

# --- 3. DATA CONTRACTS (Pydantic Models) ---
# These classes define strictly what data we accept and return.

class Message(BaseModel):
    """Represents a single message in the chat history."""
    role: str   # Must be "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    """The payload the Frontend sends to us."""
    message: str                # The current question
    history: List[Message] = [] # Previous conversation context

class ChatResponse(BaseModel):
    """The payload we send back to the Frontend."""
    response: str       # The AI's answer
    sources: List[str]  # Citations (filenames)
    latency: float      # Performance metric (in seconds)

# --- 4. LIFECYCLE MANAGER ---
# This function runs AUTOMATICALLY when the server boots up.
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 STARTUP SEQUENCE INITIATED...")
    
    # TASK A: Load the Knowledge Base (Vector DB)
    try:
        logger.info("📚 Loading Knowledge Base (FAISS)...")
        vdb = VectorDBService()
        system_state["vector_store"] = vdb.load_knowledge_base()
        
        if system_state["vector_store"]:
            logger.info(f"✅ Knowledge Base Loaded Successfully.")
        else:
            logger.error("❌ CRITICAL: Vector Store failed to load. Retrieval will fail.")
    except Exception as e:
        logger.error(f"🔥 FATAL ERROR loading Vector DB: {e}")

    # TASK B: Initialize the Brain (Llama 3 connection)
    try:
        logger.info("🧠 Connecting to Neural Core (Groq API)...")
        system_state["brain"] = SpaceBrain()
        logger.info("✅ Neural Core Online.")
    except Exception as e:
        logger.error(f"🔥 FATAL ERROR connecting to Groq: {e}")

    # Server is now running...
    yield 
    
    # TASK C: Shutdown (Clean up)
    logger.info("💤 Powering down Royce systems...")
    system_state.clear()

# --- 5. APP INITIALIZATION ---
app = FastAPI(
    title="Royce Intelligent Backend",
    version="1.0",
    description="API Layer for Space Exploration RAG Agent",
    lifespan=lifespan # Link the lifecycle manager above
)

# --- 6. ENDPOINTS ---

@app.get("/")
async def health_check():
    """Simple ping to check if server is alive."""
    return {
        "status": "online", 
        "system": "Royce v1.0", 
        "location": "Pakuro, Ogun State"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    The Core Intelligence Handler.
    Flow: Request -> Parse Memory -> Retrieve Context -> Generate Answer -> Response
    """
    start_time = time.time()
    
    # STEP 1: SAFETY CHECK
    # Ensure the AI and DB are actually loaded.
    if not system_state["vector_store"] or not system_state["brain"]:
        raise HTTPException(
            status_code=503, 
            detail="System is still initializing or failed to load. Check server logs."
        )

    # STEP 2: MEMORY RECONSTRUCTION
    # The frontend sends JSON objects (dicts). We must convert them
    # into LangChain objects (HumanMessage/AIMessage) for the Brain to understand.
    lc_history = []
    for msg in request.history:
        if msg.role == "user":
            lc_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_history.append(AIMessage(content=msg.content))
    
    # STEP 3: RETRIEVAL (RAG)
    # Search the vector database for the 3 most relevant Q&A pairs/chunks
    try:
        results = system_state["vector_store"].similarity_search(request.message, k=3)
        # Extract just the text content from the results
        context_chunks = [doc.page_content for doc in results]
    except Exception as e:
        logger.error(f"⚠️ Retrieval failed: {e}")
        # Fallback: If DB fails, send empty context so the LLM tries to answer with general knowledge
        context_chunks = []
        results = []

    # STEP 4: GENERATION
    # Send everything to Llama 3.3
    try:
        ai_reply = system_state["brain"].chat(
            query=request.message, 
            context_chunks=context_chunks, 
            history=lc_history
        )
    except Exception as e:
        logger.error(f"🔥 Generation failed: {e}")
        raise HTTPException(status_code=500, detail="Neural Core processing error.")

    # STEP 5: RETURN RESPONSE
    execution_time = time.time() - start_time
    
    return ChatResponse(
        response=ai_reply,
        # Extract the 'source' metadata (filename) if it exists, otherwise 'unknown'
        sources=[doc.metadata.get("source", "unknown") for doc in results],
        latency=round(execution_time, 2)
    )