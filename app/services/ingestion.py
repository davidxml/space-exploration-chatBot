import os
from typing import List, Dict

class IngestionEngine:
    """
    Serves as the Digestive system for the ChatBot.
    """
    def __init__(self, raw_data_path: str = "data/raw"):
        """
        Initialize the engine pointing to where the .txt files live.
        """
        self.raw_data_path = raw_data_path

    def load_and_process_files(self) -> List[Dict]:
        """
        Reads all .txt files in the raw directory.
        Parses specific 'Q: ... A: ...' format.
        Returns a list of clean 'documents' ready for the AI.
        """
        documents = []
        
        # 1. Check if directory exists
        if not os.path.exists(self.raw_data_path):
            print(f"Warning: Directory {self.raw_data_path} not found.")
            return []

        # 2. Loop through every file (planets.txt, missions.txt, etc.)
        for filename in os.listdir(self.raw_data_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.raw_data_path, filename)
                print(f"Processing: {filename}...")
                
                new_docs = self._parse_qa_file(file_path, filename)
                documents.extend(new_docs)
                
        print(f"Total Knowledge Chunks Loaded: {len(documents)}")
        return documents

    def _parse_qa_file(self, file_path: str, source_name: str) -> List[Dict]:
        """
        Custom parser for UrbanSpace data format.
        Combines Q and A into a single semantic block.
        """
        clean_docs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split by double newlines (how your data is structured)
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().splitlines()
                if not lines:
                    continue
                
                # Extract the text
                text_content = " ".join(lines)
                
                # Only keep blocks that look like data
                if "Q:" in text_content or "A:" in text_content:
                    doc = {
                        "text": text_content,
                        "metadata": {
                            "source": source_name,
                            "topic": source_name.replace(".txt", "").capitalize()
                        }
                    }
                    clean_docs.append(doc)
                    
        except Exception as e:
            print(f"Error parsing {source_name}: {e}")

        return clean_docs

if __name__ == "__main__":
    engine = IngestionEngine()
    data = engine.load_and_process_files()
    # Preview the first chunk
    if data:
        print("\n--- Sample Chunk ---")
        print(data[0])