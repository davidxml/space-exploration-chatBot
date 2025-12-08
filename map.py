import os

def print_clean_tree(startpath):
    # I added 'UrbanSpace' here to ensure it is strictly ignored
    # Also added standard venv subfolders just in case
    IGNORE = {'UrbanSpace', 'venv', '.git', '__pycache__', '.idea', '.vscode', 'Lib', 'Scripts'}

    print(f"📂 Project Structure for: {os.path.abspath(startpath)}\n")

    for root, dirs, files in os.walk(startpath):
        # This line physically prevents Python from entering the ignored folders
        dirs[:] = [d for d in dirs if d not in IGNORE]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f'{indent}├── {os.path.basename(root)}/')
        
        subindent = '│   ' * (level + 1)
        for f in files:
            # Skip python compiled files
            if not f.endswith('.pyc'): 
                print(f'{subindent}├── {f}')

if __name__ == "__main__":
    print_clean_tree('.')