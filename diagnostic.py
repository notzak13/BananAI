import os
from src.repository.batch_repository import BatchRepository
from src.models.inventory import Inventory

def diagnose():
    print("--- 🩺 BANANAI SYSTEM DIAGNOSTIC ---")
    
    # 1. Check Directory
    path = os.path.join(os.getcwd(), "data", "batches")
    print(f"[*] Checking path: {path}")
    if not os.path.exists(path):
        print("❌ ERROR: Path does not exist!")
        return
    
    files = [f for f in os.listdir(path) if f.endswith('.json')]
    print(f"[*] Raw files found on disk: {files}")

    # 2. Test Repository
    repo = BatchRepository()
    batches = repo.load_all_batches()
    print(f"[*] Repository loaded {len(batches)} batches.")

    # 3. Test Inventory
    inv = Inventory()
    for b in batches:
        inv.add_batch(b)
    
    print(f"[*] Inventory count: {len(inv.batches)}")
    
    if len(inv.batches) == 0 and len(files) > 0:
        print("\n🚨 CRITICAL FINDING: Files exist but failed to load into memory.")
        print("Check if remaining_weight_kg is 0 or if 'from_dict' is crashing.")

if __name__ == "__main__":
    diagnose()