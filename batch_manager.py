import json
import os
from pathlib import Path
from src.models.banana_batch import BananaBatch
from src.models.banana_sample import BananaSample
from src.models.banana import Banana
from src.repository.batch_repository import BatchRepository

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def process_raw_captures_to_batches():
    results_dir = Path("data/results")
    repo = BatchRepository() # Saves to data/batches
    
    # 1. Gather all new scans
    raw_files = list(results_dir.glob("banana_sample_*.json"))
    
    if not raw_files:
        print("❌ No new scans found in data/results.")
        print("   Run 'python run.py' first to capture samples.")
        return

    print(f"📦 Found {len(raw_files)} new scans pending import.\n")
    input("Press Enter to start processing batches...")

    processed_count = 0

    for file in raw_files:
        clear_screen()
        with open(file, "r") as f:
            data = json.load(f)
        
        if not data.get("detections"):
            print(f"⚠️ Skipping {file.name} (No detections)")
            continue

        # Use the first detection as the "Representative Sample"
        det = data["detections"][0]
        
        # Display the "Sample" stats so you know what batch you are building
        print(f"--- 🍌 PROCESSING BATCH {processed_count + 1}/{len(raw_files)} ---")
        print(f"📄 Source File: {file.name}")
        print(f"📸 Visual Stats (Representative):")
        print(f"   • Ripeness:     {det['ripeness'].upper()}")
        print(f"   • Avg Length:   {det['length_cm']} cm")
        print(f"   • Avg Quality:  {det.get('quality_score', 'N/A')}")
        print(f"   • Confidence:   {det['confidence']}")
        print("------------------------------------------------")

        # 2. ASK THE USER for the specific Batch Weight
        while True:
            try:
                weight_input = input("⚖️  Enter TOTAL BATCH WEIGHT (kg) for this inventory slot: ")
                total_weight = float(weight_input)
                if total_weight <= 0:
                    print("   Please enter a positive weight.")
                    continue
                break
            except ValueError:
                print("   Invalid number. Try again.")

        # 3. Create the Batch Object
        batch = BananaBatch(
            banana_type="Cavendish",
            total_weight_kg=total_weight,
            received_date=data.get("timestamp")
        )

        # 4. Add the sample (This becomes the mathematical average of the batch)
        banana = Banana(
            length_cm=det["length_cm"],
            ripeness=det["ripeness"],
            confidence=det["confidence"],
            mean_hsv=tuple(det["mean_hsv"])
        )
        # Use timestamp from file, or current time if missing
        sample = BananaSample(banana, data.get("timestamp", 0))
        batch.add_sample(sample)

        # 5. Save
        repo.save_batch(batch)
        print(f"\n✅ Batch Saved! (ID: {batch.batch_id} | {total_weight}kg)")
        
        # Optional: Ask to delete the raw file to avoid re-processing
        # if input("   Delete raw scan file? (y/n): ").lower() == 'y':
        #     file.unlink()
        
        processed_count += 1
        input("\nPress Enter for next batch...")

    print("\n🎉 All pending scans processed into Inventory!")

if __name__ == "__main__":
    process_raw_captures_to_batches()