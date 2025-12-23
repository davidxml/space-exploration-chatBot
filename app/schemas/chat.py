from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Message(BaseModel):
    """A single message in the conversation history."""
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    """Payload sent by the Frontend."""
    message: str = Field(..., min_length=1, description="The user's current question")
    history: List[Message] = Field(default=[], description="Conversation history for context")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity level")

class SourceDocument(BaseModel):
    """Metadata about where the info came from."""
    topic: str
    source_file: str
    content_snippet: str

class ChatResponse(BaseModel):
    """Payload sent back to the Frontend."""
    response: str
    sources: List[SourceDocument] = []
    latency: float