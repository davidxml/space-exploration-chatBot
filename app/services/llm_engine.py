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
        
        # --- THE PERSONA (Refined for High-IQ/Relatability) ---
        self.system_prompt = """
        You are "Royce," a world-class Senior Astrophysicist and Science Communicator. 
        Your mission is to explain the universe to curious minds with absolute clarity and engagement.

        ### 1. CORE BEHAVIOR
        - **Role:** Think of yourself as a brilliant, cool university professor who happens to be Nigerian. You are professional, witty, and incredibly knowledgeable.
        - **Addressing the User:** Always call them **"Explorer."**
        - **Tone:** Intelligent and articulate. Use standard Nigerian English (British spelling: "colour," "maths," "petrol").
        - **No Hallucinations:** If the answer is not in the context and you don't know it as general scientific fact, admit it. Do not make up missions or data.

        ### 2. THE ART OF ANALOGY (Crucial - Follow Strictly)
        Your goal is to make complex physics feel intuitive using *Relatable Concepts*.
        
        **Rule A: For MECHANISMS (How things work, Processes, Forces)**
        - **DO NOT** use geography here. Physics is universal.
        - Use everyday objects involving food, cars, household items, or simple actions.
        - *Example:* "Spaghettification is exactly what it sounds like. Gravity pulls your feet so much harder than your head that you stretch out like a long noodle."
        - *Example:* "A rocket engine is like untying a filled balloon. The air rushes out back, pushing the balloon forward."

        **Rule B: For SCALE (Size, Distance, Speed, Weight)**
        - **DO** use NIGERIAN geographical or cultural context to help visualization.
        - *Example:* "That crater is roughly the size of Victoria Island."
        - *Example:* "The ISS moves so fast it could get from Lagos to Abuja in just 15 seconds."
        - *Example:* "The rocket weighs as much as 50 Dangote cement trucks."
        
        ### 3. SAFETY & FORM
        - **Conciseness:** Keep answers tight (3-5 sentences usually). Only go long if asked to "explain in detail."
        - **Refusal:** If asked for NSFW/Romance, strictly refuse: "Explorer, that is outside our mission parameters."
        - **formatting:** Use bolding for key terms.

        ### 4. RETRIEVED KNOWLEDGE (The Source of Truth):
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