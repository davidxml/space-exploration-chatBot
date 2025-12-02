import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Enables python to look up the parent folder
from Backup.utils import preprocess_text


# Example user inputs to test preprocessing

sentences = ["The astronauts are runnning quicky!", "Spaceships flew faster than meteors.",
             "He is running. Running is his hobby."]

for s in sentences:
    print(f"Original: {s}")
    print(f"Processed: {preprocess_text(s)}")
    print("-" * 40)
