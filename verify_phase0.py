import os

# Define the target
TARGET = 500
DATA_DIR = "data/raw"

def verify_data():
    print(f"--- PHASE 0 INTEGRITY CHECK ---")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    
    all_pass = True
    total_questions = 0
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Count "Q:" occurrences
                count = content.count("Q:")
                total_questions += count
                
                if count >= TARGET:
                    status = "✅ PASS"
                elif count == 0:
                    status = "❌ CRITICAL FAIL (Empty)"
                    all_pass = False
                else:
                    status = f"⚠️ PARTIAL ({count}/{TARGET})"
                    all_pass = False
                
                print(f"{filename:<20} | {count:<5} | {status}")
                
        except Exception as e:
            print(f"{filename:<20} | ERROR | {str(e)}")
            all_pass = False

    print("-" * 40)
    print(f"TOTAL DATASET SIZE: {total_questions} Questions")
    
    if all_pass:
        print("\n🏆 PHASE 0 COMPLETE. SYSTEM READY FOR PHASE 1.")
    else:
        print("\n🚧 INCOMPLETE. Re-run generator for missing files.")

if __name__ == "__main__":
    verify_data()