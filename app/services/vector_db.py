import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.ingestion import IngestionEngine

class VectorDBService:
    """
    Manages the long-term memory of the AI.
    Converts text -> Vectors -> FAISS Database.
    """
    
    def __init__(self, db_path="data/vector_store"):
        self.db_path = db_path
        # We use 'all-MiniLM-L6-v2'. It is fast, free, and runs on your laptop CPU.
        # It creates a 384-dimensional vector for every sentence.
        print("--- Loading Embedding Model (all-MiniLM-L6-v2) ---")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def build_knowledge_base(self):
        """
        Runs the Ingestion Engine to read .txt files,
        chunks them, and builds a fresh FAISS index.
        """
        print("\n--- STARTING MEMORY BUILD ---")
        
        # 1. Ingest Data
        engine = IngestionEngine()
        raw_docs = engine.load_and_process_files()
        
        if not raw_docs:
            print("CRITICAL: No data found to ingest! Check data/raw folder.")
            return

        # 2. Chunking
        # We use 700 characters per chunk with 70 overlap.
        # This ensures the AI gets enough context (about 3-5 sentences) per search result.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=70
        )
        
        docs = text_splitter.create_documents(
            [d['text'] for d in raw_docs], 
            metadatas=[d['metadata'] for d in raw_docs]
        )
        print(f"  -> Split {len(raw_docs)} raw blocks into {len(docs)} searchable vectors.")

        # 3. Create Vector Store
        print("  -> Vectorizing data... (This uses your CPU, please wait...)")
        db = FAISS.from_documents(docs, self.embeddings)

        # 4. Save to Disk
        # This creates the 'data/vector_store' folder
        db.save_local(self.db_path)
        print(f"SUCCESS: Knowledge Base built and saved to {self.db_path}")

    def load_knowledge_base(self):
        """
        Loads the existing FAISS index from disk.
        """
        if not os.path.exists(self.db_path):
            raise ValueError(f"Vector DB not found at {self.db_path}. Run build_knowledge_base() first.")
            
        return FAISS.load_local(
            self.db_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

if __name__ == "__main__":
    # When run directly, it rebuilds the database
    vdb = VectorDBService()
    vdb.build_knowledge_base()