import json
import os
from pathlib import Path
from typing import List
from src.models.banana_batch import BananaBatch

class BatchRepository:
    def __init__(self, storage_path: str = "data/batches"):
        # This ensures we use an absolute path to avoid "Current Working Directory" confusion
        self.storage_path = Path(os.getcwd()) / storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        print(f"[*] Repository Initialized. Looking for bananas in: {self.storage_path}")

    def load_all_batches(self) -> List[BananaBatch]:
        batches = []
        files = list(self.storage_path.glob("*.json"))
        
        print(f"[*] Found {len(files)} JSON files in storage.")

        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    # Force conversion using the new Google-grade from_dict
                    batch = BananaBatch.from_dict(data)
                    batches.append(batch)
                    print(f"    - Loaded Batch: {batch.batch_id} ({batch.remaining_weight_kg}kg)")
            except Exception as e:
                print(f"    - ❌ Failed to load {file_path.name}: {e}")
        
        return batches

    def save_batch(self, batch: BananaBatch):
        file_path = self.storage_path / f"{batch.batch_id}.json"
        with open(file_path, "w") as f:
            json.dump(batch.to_dict(), f, indent=4)