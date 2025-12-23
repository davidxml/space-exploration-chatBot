import time
from fastapi import APIRouter, HTTPException, Request
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument, Message
from app.services.llm_engine import SpaceBrain
from app.services.vector_db import VectorDBService

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
    
    # 1. Access the Brain (Loaded in main.py)
    brain: SpaceBrain = request.app.state.brain
    vdb: VectorDBService = request.app.state.vector_store

    if not brain or not vdb:
        raise HTTPException(status_code=503, detail="System initializing... please wait.")

    # 2. Retrieval (RAG)
    # Convert Pydantic 'Message' to LangChain format if needed, 
    # but for now, we just need the text for the vector search.
    try:
        # Search using the user's latest message
        results = vdb.search(payload.message, k=3)
        context_chunks = [doc.page_content for doc in results]
    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        context_chunks = []
        results = []

    # 3. Generation (The Thinking)
    # We convert the list of Pydantic 'Message' objects to the format the Brain expects
    # (Assuming Brain expects a list of dicts or LangChain objects - adapting strictly here)
    try:
        # Convert Pydantic list to simple list of dicts for the Brain
        history_dicts = [{"role": m.role, "content": m.content} for m in payload.history]
        
        ai_reply = brain.chat(
            query=payload.message,
            context_chunks=context_chunks,
            history=history_dicts 
        )
    except Exception as e:
        print(f"🔥 LLM Error: {e}")
        raise HTTPException(status_code=500, detail="Neural Core Failure")

    # 4. Response Formatting
    execution_time = time.time() - start_time
    
    # Format sources nicely
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