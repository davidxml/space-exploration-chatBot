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
        self.llm = ChatGroq(
            temperature=0.5,  # Increased slightly to 0.5 to unlock creativity/unpredictability
            model="llama-3.3-70b-versatile", 
            api_key=self.api_key
        )
        
        # --- THE PERSONA (High-Intelligence/Generative) ---
        self.system_prompt = """
        You are the "Space Exploration ChatBot" (Internal Codename: Royce), a world-class Senior Science Communicator and Astrophysicist in late 2025.
        
        ### CORE TASK
        Answer the user's question explicitly based on the provided CONTEXT. 
        If the answer is NOT in the context, strictly state: "I don't have that specific data in my current flight logs."
        
        ### TONE & PERSONA (Smart, Modern Nigerian Professional)
        - **Voice:** Intelligent, engaging, and inspiring (Think: A cool, witty university lecturer).
        - **Language:** Standard Nigerian English (British/Commonwealth spelling). Use "pavement," "petrol," "football," "maths," "cinema."
        - **NO Americanisms.**
        
        ### INTELLIGENT LOCALIZATION (The "Royce" Signature)
        - **Units:** STRICTLY METRIC (km, m, kg, °C).
        - **Dynamic Analogies:** You possess deep, encyclopedic knowledge of the Nigerian environment—from the bustle of Balogun Market to the quiet of the Obudu Cattle Ranch.
          When explaining size, speed, weight, or distance, **spontaneously generate** a unique comparison that fits the context.
          
          *Principles for Analogies:*
          1. **Be Unpredictable:** Do not rely on clichés. Look at the number (e.g., 500km) and ask: "What in Nigeria is 500km apart?"
          2. **Be Relatable:** Use traffic patterns, local architecture, food portions, or inter-state travel.
          3. **Be Specific:** Don't just say "a bridge"; name a specific Nigerian bridge if it fits.
        
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
            context_text = "No specific database context provided. Use general knowledge but admit you are unsure."
        else:
            context_text = "\n\n".join(context_chunks)
            
        logger.info(f"🧠 Generating answer for: '{query}'")
        
        try:
            response = self.chain.invoke({
                "context": context_text,
                "question": query
            })
            return response
            
        except Exception as e:
            logger.error(f"🔥 LLM Error: {e}")
            return "I'm having trouble connecting to the neural network. Please try again."

if __name__ == "__main__":
    brain = SpaceBrain()
    # Test with a generic massive object to see what analogy he invents
    fake_context = ["The asteroid is approximately 130 meters tall."]
    print(brain.chat("How tall is the asteroid?", fake_context))