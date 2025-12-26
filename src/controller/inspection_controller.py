import time
from src.models.banana import Banana
from src.models.banana_sample import BananaSample
from src.models.banana_batch import BananaBatch
from src.repository.batch_repository import BatchRepository

class InspectionController:
    def __init__(self, banana_type: str = "Cavendish"):
        self.current_batch = BananaBatch(
            banana_type=banana_type,
            received_date=time.time()
        )
        self.repo = BatchRepository()

    def process_detection(self, result_dict: dict):
        """
        Takes raw CV result and adds it to the CURRENT in-memory batch.
        """
        if not result_dict:
            return

        # Create Domain Objects
        banana = Banana(
            length_cm=result_dict["length_cm"],
            ripeness=result_dict["ripeness"],
            confidence=result_dict["confidence"],
            mean_hsv=result_dict["mean_hsv"]
        )
        
        sample = BananaSample(banana, time.time())
        
        # Add to the current working batch
        self.current_batch.add_sample(sample)
        print(f"🍌 Sample added. Batch count: {len(self.current_batch)}")

    def finalize_batch(self, total_weight_kg: float):
        """
        Called when scanning is done. 
        Assigns the simulated weight and saves to permanent inventory.
        """
        if len(self.current_batch) == 0:
            print("❌ Cannot save empty batch.")
            return

        self.current_batch.total_weight_kg = total_weight_kg
        self.current_batch.remaining_weight_kg = total_weight_kg
        
        # Save to filesystem
        self.repo.save_batch(self.current_batch)
        print(f"📦 Batch {self.current_batch.batch_id} finalized and saved.")
        
        # Reset for next scan
        self.current_batch = BananaBatch(
            banana_type=self.current_batch.banana_type,
            received_date=time.time()
        )