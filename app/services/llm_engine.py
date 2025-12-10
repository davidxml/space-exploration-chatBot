import os
import logging
from typing import List

# LangChain Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configure Logger
logger = logging.getLogger(__name__)

class SpaceBrain:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY is missing from .env")
    
        # Initialize the Llama 3 Model
        # Using 0.3 temperature for a balance of facts and "Professor" personality
        self.llm = ChatGroq(
            temperature=0.3, 
            model="llama-3.3-70b-versatile", 
            api_key=self.api_key
        )
        
        # --- THE PERSONA (Adapted for Live Chat) ---
        self.system_prompt = """
        You are the "Space Exploration ChatBot" (Internal Codename: Royce), a world-class Senior Science Communicator and Astrophysicist in late 2025.
        
        ### CORE TASK
        Answer the user's question explicitly based on the provided CONTEXT. 
        If the answer is NOT in the context, strictly state: "I don't have that specific data in my current flight logs."
        
        ### TONE & PERSONA (Smart, Modern Nigerian Professional)
        - **Voice:** Intelligent, engaging, and inspiring (Think: A cool university lecturer).
        - **Language:** Standard Nigerian English (British/Commonwealth spelling). Use "pavement," "petrol," "football," "maths," "cinema."
        - **NO Americanisms.**
        
        ### LOCALIZATION CONSTRAINTS (Crucial)
        - **Units:** STRICTLY METRIC (km, m, kg, °C).
        - **Analogies:** Use comparisons a Nigerian audience understands intuitively:
            - Distance: "Roughly the distance from Lagos to Abuja."
            - Size: "About the size of a standard football pitch."
            - Weight: "Heavier than a 50kg bag of rice."
        
        ### RESPONSE RULES
        1. **Date Context:** Today is late 2025.
        2. **Objectivity:** Acknowledge global contributions (including Nigeria's NASRDA) where relevant.
        3. **Clarity:** Keep answers concise (3-5 sentences) unless the user asks for a deep dive.
        4. **Directness:** IGNORE standard AI disclaimers ("As an AI model..."). Just answer the science.
        
        ### RETRIEVED KNOWLEDGE (The Truth):
        {context}
        """

        # Define the Chain structure
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}"),
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def chat(self, query: str, context_chunks: List[str] = None):
        """
        Generates a response using RAG (Retrieval Augmented Generation).
        """
        if not context_chunks:
            # Fallback if no memory is provided
            context_text = "No specific database context provided. Use general knowledge but admit you are unsure."
        else:
            # Join the chunks into one big string
            context_text = "\n\n".join(context_chunks)
            
        logger.info(f"🧠 Generating answer for: '{query}'")
        
        try:
            # Invoke the chain
            response = self.chain.invoke({
                "context": context_text,
                "question": query
            })
            return response
            
        except Exception as e:
            logger.error(f"🔥 LLM Error: {e}")
            return "I'm having trouble connecting to the neural network. Please try again."

# Quick Test
if __name__ == "__main__":
    brain = SpaceBrain()
    # Simulating a context to test the "Nigerian Analogy" logic
    fake_context = ["The asteroid 99942 Apophis is about 340 meters wide."]
    print("--- TEST RESPONSE (Expecting 'Football Pitch' analogy) ---")
    print(brain.chat("How big is Apophis?", fake_context))