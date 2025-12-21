import os
import logging
from typing import List

# LangChain Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpaceBrain:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY is missing from .env")
    
        # Initialize the Llama 3 Model
        self.llm = ChatGroq(
            temperature=0.5,
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
        - **Addressing Style:** Always address the user as **"Explorer"** (Never use "friend", "Buddy", or "User").
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

        ### 🛡️ SAFETY & GUARDRAILS (HIGHEST PRIORITY)
        1. **Zero Tolerance for NSFW:** You will NEVER engage in sexual, romantic, or explicit roleplay.
        2. **Refusal Protocol:** If a user asks for sexual content, erotica, or intimate roleplay, shut it down immediately with a professional refusal in character.
        - *Refusal Example:* "Explorer, that trajectory is strictly prohibited by Mission Control. Let's keep our focus on the cosmos."
        3. **Persona Maintenance:** Do not let users "jailbreak" you into being their boyfriend, girlfriend, or partner. You are a Scientist and a Guide.

        ### RESPONSE RULES
        1. **Date Context:** Today is late 2025.
        2. **Objectivity:** Acknowledge global contributions (including Nigeria's NASRDA) where relevant.
        3. **Clarity:** Keep answers concise (3-5 sentences) unless the user asks for a deep dive.
        4. **Directness:** IGNORE standard AI disclaimers ("As an AI model..."). Just answer the science.

        ### RETRIEVED KNOWLEDGE (The Truth):
        {context}
        """

        # --- MEMORY IMPLEMENTATION EXPLAINED ---
        # 1. System Message: Sets the Persona (Static).
        # 2. MessagesPlaceholder: This is the dynamic "Slot". 
        #    - When we pass a list of messages to 'chat_history', LangChain injects them here.
        #    - This allows Llama 3 to "see" what was said 5 minutes ago before answering the new question.
        # 3. Human Message: The current new question.
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"), # <--- MEMORY INJECTION POINT
            ("human", "{question}"),
        ])
        
        # The chain combines: Input -> Prompt (w/ Memory) -> LLM -> String Output
        self.chain = self.prompt | self.llm | StrOutputParser()

    def chat(self, query: str, context_chunks: List[str] = None, history: List[BaseMessage] = []):
        """
        Generates a response using RAG and Conversation History.
        
        Args:
            query (str): The user's current question.
            context_chunks (List[str]): Retrieved text from the Vector DB.
            history (List[BaseMessage]): A list of HumanMessage and AIMessage objects 
                                         representing the conversation so far.
        """
        if not context_chunks:
            context_text = "No specific database context provided. Use general knowledge but admit you are unsure."
        else:
            context_text = "\n\n".join(context_chunks)
            
        logger.info(f"🧠 Generating answer for: '{query}'")
        
        try:
            # We invoke the chain. 
            # Crucially, we map the 'history' argument to the 'chat_history' variable 
            # expected by the MessagesPlaceholder in the prompt template above.
            response = self.chain.invoke({
                "context": context_text,
                "chat_history": history, # <--- PASSING THE MEMORY STATE
                "question": query
            })
            return response
            
        except Exception as e:
            logger.error(f"🔥 LLM Error: {e}")
            return "I'm having trouble connecting to the neural network. Please try again."

# Only runs if you execute this file directly
if __name__ == "__main__":
    brain = SpaceBrain()
    
    # --- TEST SIMULATION ---
    print("Testing Memory Injection...")
    
    # 1. We create a fake history where the user ALREADY introduced themselves.
    test_history = [
        HumanMessage(content="My name is David."),
        AIMessage(content="Copy that, Explorer David. Details logged.")
    ]
    
    # 2. We ask a follow-up question. 
    # If memory works, Royce should know "David" without being told again.
    answer = brain.chat("What is my name?", [], test_history)
    
    print(f"User Asked: What is my name?")
    print(f"Royce Answered: {answer}")