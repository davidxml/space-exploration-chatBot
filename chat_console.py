import sys
import os
import time

# --- PATH FIX ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.vector_db import VectorDBService
from app.services.llm_engine import SpaceBrain
# 1. NEW IMPORT: Essential for Memory
from langchain_core.messages import HumanMessage, AIMessage 

def main():
    print("\n🚀 INITIALIZING SPACE EXPLORATION CHATBOT...")
    
    # 1. Initialize the Librarian (Vector DB)
    print("   -> Loading Knowledge Base...")
    vdb = VectorDBService()
    vector_store = vdb.load_knowledge_base()
    
    if not vector_store:
        print("❌ CRITICAL: Could not load Vector DB. Run 'python -m app.services.vector_db' first.")
        return

    # 2. Initialize the Brain (LLM)
    print("   -> Waking up Neural Core (Llama 3.3)...")
    try:
        brain = SpaceBrain()
    except Exception as e:
        print(f"❌ Error initializing Brain: {e}")
        return
    
    print("\n✅ SYSTEM ONLINE. (Type 'quit' to exit)")
    print("-" * 50)

    # 3. NEW: Initialize Memory List
    chat_history = [] 

    # 4. The Chat Loop
    while True:
        user_input = input("\n🧑 YOU: ")
        
        if user_input.lower() in ["quit", "exit"]:
            print("🤖 ROYCE: Signing off. Safe travels! 🚀")
            break
            
        start_time = time.time()
        
        # --- PHASE 1: RETRIEVAL ---
        # Find the 3 most relevant pages in our book
        results = vector_store.similarity_search(user_input, k=3)
        
        # Extract just the text from the results
        context_chunks = [doc.page_content for doc in results]
        
        # --- PHASE 2: GENERATION (WITH MEMORY) ---
        # 5. FIXED: Feed the question + text + HISTORY to the Brain
        response = brain.chat(user_input, context_chunks, chat_history)
        
        elapsed = time.time() - start_time
        
        print(f"🤖 ROYCE: {response}")
        print(f"   (Latency: {elapsed:.2f}s | Sources Found: {len(results)})")
        
        # 6. NEW: Update Memory
        # Add the interaction to the history list
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))
        
        # Keep memory short (e.g., last 6 turns) to save tokens/cost
        if len(chat_history) > 6:
            chat_history = chat_history[-6:]

if __name__ == "__main__":
    main()