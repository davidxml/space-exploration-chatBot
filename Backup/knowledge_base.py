import os

def load_knowledge_base(directory_path):
    """
    Loads all .txt files from the given directory, parses Q/A pairs, and returns a list of dicts:
    [
        {"question": "...", "answer": "..."},
        ...
    ]
    Assumes each Q/A pair in the file is formatted as:
    Q: ...\nA: ...\n (blank line between pairs)
    """

    knowledge = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)  # Full path to file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Split into blocks by blank lines
            blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
            for block in blocks:
                lines = block.splitlines()
                question, answer = None, None
                for line in lines:
                    if line.startswith('Q:'):
                        question = line[2:].strip()
                    elif line.startswith('A:'):
                        answer = line[2:].strip()
                if question and answer:
                    knowledge.append({"question": question, "answer": answer})
    return knowledge

