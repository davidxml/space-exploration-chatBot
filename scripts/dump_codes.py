import os

# --- Configuration ---
OUTPUT_FILE = "curr_prog.txt"
ROOT_DIR = os.path.abspath(".")

# Directory name patterns to ignore ANYWHERE in the tree
IGNORE_DIR_NAMES = {
    "venv",
    ".venv",
    "env",
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
    "Backup"
}

# Files to ignore
IGNORE_FILES = {
    OUTPUT_FILE,
    ".env",
    ".gitignore",
    "index.faiss",
    "index.pkl",
    "dump_code.py"
}

# Allowed file extensions
INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
    ".json",
    ".yml",
    ".yaml"
}


def should_ignore_path(path: str) -> bool:
    """
    Returns True if any part of the path matches ignored directory names
    """
    parts = os.path.normpath(path).split(os.sep)
    return any(part in IGNORE_DIR_NAMES for part in parts)


def generate_manifest():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(ROOT_DIR, topdown=True):

            # --- HARD STOP: skip entire subtree if path contains venv ---
            if should_ignore_path(dirpath):
                dirnames.clear()
                continue

            # --- Prune directories BEFORE walking into them ---
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORE_DIR_NAMES
            ]

            for filename in filenames:
                if filename in IGNORE_FILES:
                    continue

                _, ext = os.path.splitext(filename)
                if ext.lower() not in INCLUDE_EXTENSIONS:
                    continue

                filepath = os.path.join(dirpath, filename)

                # Final safety check
                if should_ignore_path(filepath):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as infile:
                        content = infile.read()

                    outfile.write("=" * 80 + "\n")
                    outfile.write(f"FILE PATH: {filepath}\n")
                    outfile.write("=" * 80 + "\n")
                    outfile.write(content + "\n\n")

                    print(f"Processed: {filepath}")

                except Exception as e:
                    print(f"Skipped {filepath}: {e}")


if __name__ == "__main__":
    generate_manifest()
    print(f"\nSuccessfully generated {OUTPUT_FILE}")
