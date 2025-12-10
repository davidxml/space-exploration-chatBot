# FILE: test_retrieval.py
import sys
import os

# --- PATH FIX (Standard for VS Code execution) ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.vector_db import VectorDBService

def run_sanity_check():
    print("\n--- 🕵️‍♀️ STARTING RETRIEVAL SANITY CHECK ---")
    
    # 1. Load the Database (No rebuilding, just loading)
    vdb = VectorDBService()
    vector_store = vdb.load_knowledge_base()
    
    if not vector_store:
        print("❌ Error: Could not load Vector DB.")
        return

    # 2. Define a Test Query
    # This specific question should match content in 'blackholes.txt'
    test_query = "What happens if you fall into a black hole?"
    
    print(f"\n❓ QUERY: '{test_query}'")
    print("... Searching 3,381 vectors for the best match ...\n")
    
    # 3. Perform the Search (k=3 means 'get top 3 matches')
    results = vector_store.similarity_search(test_query, k=3)
    
    # 4. Display Results
    for i, doc in enumerate(results):
        print(f"--- MATCH #{i+1} (Source: {doc.metadata.get('source', 'Unknown')}) ---")
        print(f"📄 CONTENT: {doc.page_content[:300]}...") # Print first 300 chars
        print("-" * 50)

if __name__ == "__main__":
    run_sanity_check()