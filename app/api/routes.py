import time
from fastapi import APIRouter, HTTPException, Request

# Data Models
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument

# LangChain Types (Crucial for the fix)
from langchain_core.messages import HumanMessage, AIMessage

# Create the Router
router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple ping to check if the brain is alive."""
    return {"status": "online", "system": "Royce v1.1"}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    The Main Communication Link.
    Receives JSON -> Decodes -> Thinks -> Responds.
    """
    start_time = time.time()
    
    # --- 1. STARTUP CHECKS ---
    # Access the Brain and DB that were loaded in main.py
    brain = getattr(request.app.state, "brain", None)
    vdb = getattr(request.app.state, "vector_store", None)

    if not brain or not vdb:
        raise HTTPException(status_code=503, detail="System initializing... please wait.")

    # --- 2. RETRIEVAL (RAG) ---
    try:
        # We try the safe 'search' method first
        if hasattr(vdb, "search"):
            results = vdb.search(payload.message, k=3)
        # Fallback to direct index access if 'search' wrapper is missing
        elif hasattr(vdb, "load_knowledge_base"):
             idx = vdb.load_knowledge_base()
             results = idx.similarity_search(payload.message, k=3)
        else:
             results = []
        
        context_chunks = [doc.page_content for doc in results]
    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        context_chunks = []
        results = []

    # --- 3. HISTORY TYPE FIX ---
    # Convert Pydantic models -> LangChain Objects
    lc_history = []
    for msg in payload.history:
        if msg.role == "user":
            lc_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_history.append(AIMessage(content=msg.content))
        # Note: We ignore 'system' messages here as the Brain manages its own persona.
    
    # --- 4. GENERATION ---
    try:
        ai_reply = brain.chat(
            query=payload.message,
            context_chunks=context_chunks,
            history=lc_history  # <--- PASSING CORRECT OBJECTS
        )
    except Exception as e:
        print(f"🔥 LLM Error: {e}")
        raise HTTPException(status_code=500, detail="Neural Core Failure")

    # --- 5. RESPONSE FORMATTING ---
    execution_time = time.time() - start_time
    
    # Format sources nicely for the UI
    source_docs = []
    for doc in results:
        source_docs.append(SourceDocument(
            topic=doc.metadata.get("topic", "General"),
            source_file=doc.metadata.get("source", "Unknown"),
            content_snippet=doc.page_content[:100] + "..."
        ))

    return ChatResponse(
        response=ai_reply,
        sources=source_docs,
        latency=round(execution_time, 2)
    )