import time
from models.banana import Banana
from models.banana_sample import BananaSample
from models.banana_batch import BananaBatch

class InspectionController:
    def __init__(self, banana_type: str):
        self.batch = BananaBatch(banana_type)

    def register_sample(self, result_dict):
        banana = Banana(
            length_cm=result_dict["length_cm"],
            ripeness=result_dict["ripeness"],
            confidence=result_dict["confidence"],
            mean_hsv=result_dict["mean_hsv"]
        )
        sample = BananaSample(banana, time.time())
        self.batch.add_sample(sample)
