import json
from pathlib import Path
from src.models.banana import Banana
from src.models.banana_sample import BananaSample
from src.models.banana_batch import BananaBatch


class BatchRepository:
    def __init__(self, data_dir="data/results"):
        self.data_dir = Path(data_dir)

    def load_batch(self, banana_type: str) -> BananaBatch:
        batch = BananaBatch(banana_type)

        for file in self.data_dir.glob("banana_sample_*.json"):
            with open(file, "r") as f:
                data = json.load(f)

            # ---- VALIDATION ----
            if "detections" not in data or not data["detections"]:
                continue

            for det in data["detections"]:
                try:
                    banana = Banana(
                        length_cm=det["length_cm"],
                        ripeness=det["ripeness"],
                        confidence=det["confidence"],
                        mean_hsv=tuple(det["mean_hsv"]),
                    )

                    sample = BananaSample(
                        banana=banana,
                        timestamp=data.get("timestamp", 0),
                    )

                    batch.add_sample(sample)

                except KeyError:
                    # Skip malformed detection
                    continue

        if len(batch) == 0:
            raise RuntimeError("No valid banana samples found.")

        return batch
