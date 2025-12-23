import os
import sys
import shutil
import logging
import stat
from typing import Optional

# LangChain Imports
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- PATH FIX: Allow running this file directly ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Local Modules
from app.services.ingestion import IngestionEngine

# Configure Professional Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorDBService:
    """
    The Cortex of UrbanSpace. 
    Manages embedding generation and vector storage.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initializes the Vector Service.
        """
        # Local import to avoid circular dependency with config.py
        from app.core.config import settings
        
        # Use passed path OR default from settings
        self.db_path = db_path if db_path else settings.VECTOR_DB_PATH
        
        # --- FIX 1: Initialize index to None ---
        # This prevents "access-member-before-definition" errors in Pylint
        self.index = None
        
        # Model Configuration
        self.embedding_model_name = settings.EMBEDDING_MODEL
        
        logger.info(f"🔌 Initializing Embedding Model: {self.embedding_model_name}")
        # Running on CPU? This model is optimized for it.
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)

    def search(self, query: str, k: int = 3):
        """
        Safe wrapper for searching the vector index.
        Used by routes.py to avoid direct access to FAISS internals.
        """
        # 1. Check if index is loaded in memory
        if self.index is None:
            # 2. Try to load it from disk
            self.index = self.load_knowledge_base()
        
        # 3. Perform search if index exists
        if self.index:
            return self.index.similarity_search(query, k=k)
        
        # 4. Return empty list if DB is broken/missing
        return []

    def build_knowledge_base(self, force_clean: bool = True):
        """
        Orchestrates the complete rebuilding of the Vector Database.
        Includes a Windows-specific fix for Permission Errors.
        """
        logger.info("🚀 STARTING KNOWLEDGE BASE BUILD PROTOCOL")

        # --- WINDOWS FIX: Force Delete Handler ---
        def remove_readonly(func, path, _):
            "Clear the Read-Only bit and re-attempt the deletion"
            os.chmod(path, stat.S_IWRITE)
            func(path)

        # 1. CLEAN SLATE PROTOCOL
        if force_clean and os.path.exists(self.db_path):
            logger.warning(f"🧹 Removing old vector store at {self.db_path}...")
            try:
                # We use onexc (Python 3.12+) or onerror (older)
                shutil.rmtree(self.db_path, onexc=remove_readonly)
            except TypeError:
                shutil.rmtree(self.db_path, onerror=remove_readonly)
            except Exception as e:
                logger.warning(f"⚠️ Could not delete folder automatically (Locked?): {e}")
                logger.warning("➡️ Please manually delete 'data/vector_store' and try again.")
                return

        # 2. INGESTION
        engine = IngestionEngine()
        raw_data_dicts = engine.load_and_process_files()
        
        if not raw_data_dicts:
            logger.error("❌ CRITICAL: No raw data found. Aborting build.")
            return

        # 3. CONVERSION
        documents = [
            Document(page_content=d["text"], metadata=d["metadata"]) 
            for d in raw_data_dicts
        ]
        
        # 4. CHUNKING
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""] 
        )
        
        final_docs = text_splitter.split_documents(documents)
        logger.info(f"📊 Processing Stats: {len(documents)} Raw Blocks -> {len(final_docs)} Vectorized Chunks")

        # 5. EMBEDDING & INDEXING
        logger.info("🧠 Vectorizing data (This uses CPU, may take a moment)...")
        
        try:
            db = FAISS.from_documents(final_docs, self.embeddings)
            db.save_local(self.db_path)
            # --- FIX 2: Update self.index immediately after building ---
            self.index = db
            
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
        try:
            # --- FIX 3: Assign to self.index ---
            self.index = FAISS.load_local(
                self.db_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            return self.index
        except Exception as e:
            logger.error(f"❌ Failed to load Vector DB: {e}")
            return None

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # When run directly, we trigger the build.
    service = VectorDBService()
    service.build_knowledge_base()