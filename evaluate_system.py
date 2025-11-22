import pandas as pd
import requests
import json
from sklearn.model_selection import train_test_split
import time
import concurrent.futures
import threading

# Configuration
DATASET_PATH = 'stunting_prediction_project/stunting_wasting_dataset.csv'
API_URL = 'http://127.0.0.1:5000/predict'
# SAMPLE_SIZE = 100  # Removed for full evaluation

# Thread-safe counters
stats = {
    "correct": 0,
    "total": 0,
    "errors": 0,
    "processed": 0
}
stats_lock = threading.Lock()

def process_row(row):
    # Prepare payload
    payload = {
        "usia_bulan": int(row['Umur (bulan)']),
        "tinggi_badan": float(row['Tinggi Badan (cm)']),
        "berat_badan": float(row['Berat Badan (kg)']),
        "gender": row['Jenis Kelamin']
    }

    expected_status = row['Stunting']
    
    expected_binary = "Unknown"
    if expected_status in ['Normal', 'Tall', 'Normal weight']:
        expected_binary = "Normal"
    elif expected_status in ['Stunted', 'Severely Stunted', 'Pendek', 'Sangat Pendek']:
        expected_binary = "Stunting"
        
    is_match = False
    is_error = False
    
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            predicted_status = result['status']
            is_match = (predicted_status == expected_binary)
        else:
            is_error = True
    except Exception:
        is_error = True
        
    with stats_lock:
        stats["total"] += 1
        stats["processed"] += 1
        if is_error:
            stats["errors"] += 1
        elif is_match:
            stats["correct"] += 1
            
        if stats["processed"] % 1000 == 0:
            print(f"Processed: {stats['processed']}...")

def evaluate():
    print(f"Loading dataset from {DATASET_PATH}...")
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("Error: Dataset file not found.")
        return

    # Split 80-20
    print("Splitting data 80-20...")
    _, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    print(f"Total test set size: {len(test_df)}")
    print("Starting full evaluation with parallel requests (Max Workers: 10)...")
    print("-" * 60)

    start_time = time.time()
    
    # Convert DataFrame rows to a list of dicts for iteration
    rows = [row for _, row in test_df.iterrows()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_row, rows)

    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 60)
    if stats["total"] > 0:
        accuracy = (stats["correct"] / stats["total"]) * 100
        print(f"\nFull Evaluation Complete.")
        print(f"Time Taken: {duration:.2f} seconds")
        print(f"Total Tested: {stats['total']}")
        print(f"Correct: {stats['correct']}")
        print(f"Errors (API/Net): {stats['errors']}")
        print(f"Accuracy: {accuracy:.2f}%")
    else:
        print("No tests completed.")

if __name__ == "__main__":
    evaluate()
