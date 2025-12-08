import os
import shutil
import logging
from typing import List, Optional

# LangChain Imports
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Local Modules
from app.services.ingestion import IngestionEngine

# --- CONFIGURATION ---
DB_PATH = "data/vector_store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# Increased to 1500 to keep Q&A pairs intact (Atomic Units).
# Overlap ensures if we DO split, context isn't lost at the seam.
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

# Configure Professional Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorDBService:
    """
    The Cortex of UrbanSpace. 
    Manages embedding generation and vector storage.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        
        logger.info(f"🔌 Initializing Embedding Model: {EMBEDDING_MODEL}")
        # Running on CPU? This model is optimized for it.
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    def build_knowledge_base(self, force_clean: bool = True):
        """
        Orchestrates the complete rebuilding of the Vector Database.
        
        Args:
            force_clean (bool): If True, deletes existing DB to prevent duplicates.
        """
        logger.info("🚀 STARTING KNOWLEDGE BASE BUILD PROTOCOL")

        # 1. CLEAN SLATE PROTOCOL
        if force_clean and os.path.exists(self.db_path):
            logger.warning(f"🧹 Removing old vector store at {self.db_path} for a clean build...")
            shutil.rmtree(self.db_path)

        # 2. INGESTION
        engine = IngestionEngine()
        raw_data_dicts = engine.load_and_process_files()
        
        if not raw_data_dicts:
            logger.error("❌ CRITICAL: No raw data found. Aborting build.")
            return

        # 3. CONVERSION (Dict -> Document Objects)
        # We explicitly convert dictionaries to LangChain 'Document' objects here
        # so we have full control before splitting.
        documents = [
            Document(page_content=d["text"], metadata=d["metadata"]) 
            for d in raw_data_dicts
        ]
        
        # 4. CHUNKING (The "Safety Net")
        # We use a larger chunk size to respect the atomic nature of Q&A pairs.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""] # Prioritize splitting by double newlines
        )
        
        # This will only split if a specific Q&A block is > 1500 chars
        final_docs = text_splitter.split_documents(documents)
        
        logger.info(f"📊 Processing Stats: {len(documents)} Raw Blocks -> {len(final_docs)} Vectorized Chunks")

        # 5. EMBEDDING & INDEXING
        logger.info("🧠 Vectorizing data (This uses CPU, may take a moment)...")
        
        try:
            db = FAISS.from_documents(final_docs, self.embeddings)
            db.save_local(self.db_path)
            logger.info(f"✅ SUCCESS: Knowledge Base saved to '{self.db_path}'")
            logger.info(f"✅ Total Vectors Indexed: {db.index.ntotal}")
        except Exception as e:
            logger.critical(f"🔥 FATAL ERROR during vectorization: {e}")

    def load_knowledge_base(self) -> Optional[FAISS]:
        """
        Loads the existing FAISS index from disk for inference.
        """
        if not os.path.exists(self.db_path):
            logger.error(f"❌ Vector DB not found at {self.db_path}. Run build_knowledge_base() first.")
            return None
            
        logger.info("📂 Loading Vector Database from disk...")
        return FAISS.load_local(
            self.db_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # When run directly, we trigger the build.
    service = VectorDBService()
    service.build_knowledge_base()