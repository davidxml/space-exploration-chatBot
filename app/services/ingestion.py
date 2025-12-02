import os
from typing import List, Dict

class IngestionEngine:
    """
    Handles the loading and parsing of raw text data from the file system.
    Converts unstructured text files into structured Document objects for vector storage.
    """

    def __init__(self, raw_data_path: str = "data/raw"):
        """
        Initializes the IngestionEngine.

        Args:
            raw_data_path (str): The relative path to the directory containing .txt files.
        """
        self.raw_data_path = raw_data_path

    def load_and_process_files(self) -> List[Dict]:
        """
        Iterates through the raw data directory, reads all .txt files, and processes
        them into a list of structured dictionaries.

        Returns:
            List[Dict]: A list of document dictionaries containing 'text' and 'metadata'.
        """
        documents = []
        
        # Verify directory existence before processing
        if not os.path.exists(self.raw_data_path):
            print(f"Warning: Directory {self.raw_data_path} not found.")
            return []

        # Iterate through files in the specified directory
        for filename in os.listdir(self.raw_data_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.raw_data_path, filename)
                print(f"Processing: {filename}...")
                
                # Parse the individual file
                new_docs = self._parse_qa_file(file_path, filename)
                documents.extend(new_docs)
                
        print(f"Total Knowledge Chunks Loaded: {len(documents)}")
        return documents

    def _parse_qa_file(self, file_path: str, source_name: str) -> List[Dict]:
        """
        Parses a file containing Q&A blocks separated by double newlines.
        
        Structure expected:
        Q: [Question]
        A: [Answer]
        
        Args:
            file_path (str): Full path to the file.
            source_name (str): Name of the file (used for metadata).

        Returns:
            List[Dict]: Extracted documents.
        """
        clean_docs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split content by double newlines to isolate Q&A pairs
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().splitlines()
                if not lines:
                    continue
                
                # Flatten lines into a single string for storage
                text_content = " ".join(lines)
                
                # Filter for valid data blocks containing Question identifiers
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

# --- Execution Entry Point (For testing module in isolation) ---
if __name__ == "__main__":
    engine = IngestionEngine()
    # Trigger the load process and print the first result for verification
    data = engine.load_and_process_files()
    if data:
        print("\n--- Sample Chunk ---")
        print(data[0])