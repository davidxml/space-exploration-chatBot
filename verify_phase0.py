import os
import time
from datetime import datetime

# Define the target
TARGET = 500
DATA_DIR = "data/raw"

def format_time(timestamp):
    """Formats a timestamp for professional logging."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

def count_existing_questions(filepath):
    """Scans the file and counts how many 'Q:' lines exist."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.count("Q:")
    except:
        return 0

def verify_data():
    
    # 1. INITIALIZE AUDIT
    start_time = time.time()
    
    # Check if DATA_DIR exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ CRITICAL ERROR: Data directory '{DATA_DIR}' not found.")
        print("Please ensure the folder exists and is populated.")
        return

    print(f"\n=======================================================")
    print(f"|  PHASE 0 INTEGRITY AUDIT (Execution Log)           |")
    print(f"=======================================================")
    print(f"| TIME STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | TARGET: {TARGET} Q/File |")
    print(f"=======================================================\n")
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    files.sort()
    
    # 2. DATA PROCESSING LOOP
    total_q = 0
    all_pass = True
    processed_count = 0
    files_fully_complete = 0

    print(f"{'FILENAME':<25} | {'COUNT':<10} | {'STATUS'}")
    print("-" * 50)

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        processed_count += 1
        
        # Get file size safely
        try:
            file_size_kb = os.path.getsize(filepath) / 1024
        except:
            file_size_kb = 0.0

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count "Q:" occurrences (The metric for data points)
            count = content.count("Q:")
            total_q += count
            
            percentage = int((count / TARGET) * 100)
            
            if count >= TARGET:
                status = f"✅ {percentage}% READY"
                files_fully_complete += 1
            elif count == 0:
                status = "❌ EMPTY"
                all_pass = False
            else:
                # Using the Unicode warning triangle for clarity
                status = f"⚠️  Moderate ({percentage}%)"
                # We can proceed with LOW status, but we must update all_pass status
            
            # Print row for the main table
            print(f"{filename:<25} | {count:<10} | {status} (Size: {file_size_kb:.1f} KB)")
            
        except Exception as e:
            print(f"{filename:<25} | ❌ ERROR    | Failed to read file: {str(e)}")
            all_pass = False
            
    end_time = time.time()
    
    # 3. SUMMARY CARD GENERATION
    
    # Override all_pass ONLY IF everything is ready (since you want to proceed regardless)
    # We set a custom status based on the strict check:
    if files_fully_complete == len(files):
        overall_status_text = "SUCCESS: ALL TARGETS MET"
        status_symbol = "🟢"
        all_pass_final = True
    else:
        overall_status_text = "PARTIAL SUCCESS: SYSTEM READY TO PROCEED"
        status_symbol = "🟡"
        all_pass_final = False

    print("\n" + "=" * 50)
    print(f"| {status_symbol} AUDIT SUMMARY CARD (PHASE 0 CONCLUSION) {status_symbol} |")
    print("=" * 50)
    print(f"| **TOTAL KNOWLEDGE CHUNKS**: {total_q:,} Questions")
    print(f"| **TARGET REQUIREMENT**:     {TARGET * len(files):,} Questions")
    print(f"| **FILES FULLY COMPLETE**:   {files_fully_complete} / {len(files)}")
    print(f"| **EXECUTION TIME**:         {(end_time - start_time):.2f} seconds")
    print(f"| **FINAL STATUS**:           {(total_q/(TARGET * len(files)) * 100)} % COMPLETED! {overall_status_text}")
    print("=" * 50)

if __name__ == "__main__":
    verify_data()