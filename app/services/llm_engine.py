import os
from langchain_groq import ChatGroq

class SpaceBrain:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")
            
        # Using the new, smarter Llama 3.3 model
        self.llm = ChatGroq(
            temperature=0.3, 
            model="llama-3.3-70b-versatile", 
            api_key=self.api_key
        )

    def chat(self, user_query: str):
        """
        Simple chat interface for Phase 0.
        Later, we will upgrade this method to use RAG (Vector DB).
        """
        response = self.llm.invoke(user_query)
        return response.content