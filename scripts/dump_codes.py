import os

# --- Configuration ---
OUTPUT_FILE = "curr_prog.txt"
ROOT_DIR = "."  # Current directory

# Folders to completely ignore
IGNORE_DIRS = {
    "UrbanSpace", 
    ".venv", 
    "env", 
    ".git", 
    "__pycache__", 
    ".idea", 
    ".vscode",
    "Backup" # Optional: Remove this if you WANT the backup files included
}

# specific files to ignore
IGNORE_FILES = {
    OUTPUT_FILE, 
    ".env", 
    ".gitignore", 
    "index.faiss", 
    "index.pkl",
    "dump_code.py" # Ignores itself
}

# File extensions to include (to avoid dumping images or binaries)
INCLUDE_EXTENSIONS = {
    ".py",  
    ".md", 
    ".json", 
    ".yml", 
    ".yaml"
}

def generate_manifest():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Walk through the directory tree
        for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
            # Modify dirnames in-place to skip ignored directories
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            for filename in filenames:
                if filename in IGNORE_FILES:
                    continue
                
                # Check extension
                _, ext = os.path.splitext(filename)
                if ext.lower() not in INCLUDE_EXTENSIONS:
                    continue
                
                filepath = os.path.join(dirpath, filename)
                
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        content = infile.read()
                        
                    # Write Header and Content
                    outfile.write("=" * 80 + "\n")
                    outfile.write(f"FILE PATH: {filepath}\n")
                    outfile.write("=" * 80 + "\n")
                    outfile.write(content + "\n\n")
                    
                    print(f"Processed: {filepath}")
                    
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    generate_manifest()
    print(f"\nSuccessfully generated {OUTPUT_FILE}")