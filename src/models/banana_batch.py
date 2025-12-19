from typing import List, Dict
from .banana_sample import BananaSample


class BananaBatch:
    def __init__(self, banana_type: str):
        self.banana_type = banana_type
        self.samples: List[BananaSample] = []

    def add_sample(self, sample: BananaSample):
        self.samples.append(sample)

    # ---------- Aggregations ----------

    def average_length(self) -> float:
        return round(
            sum(s.banana.length_cm for s in self.samples) / len(self.samples), 2
        ) if self.samples else 0.0

    def average_quality(self) -> float:
        return round(
            sum(s.banana.quality_index() for s in self.samples) / len(self.samples), 2
        ) if self.samples else 0.0

    def average_weight(self) -> float:
        return round(
            sum(s.banana.estimated_weight_g() for s in self.samples) / len(self.samples),
            2
        ) if self.samples else 0.0

    def ripeness_distribution(self) -> Dict[str, int]:
        dist = {}
        for s in self.samples:
            r = s.banana.ripeness
            dist[r] = dist.get(r, 0) + 1
        return dist

    def estimated_shelf_life_days(self) -> int:
        dist = self.ripeness_distribution()
        if not dist:
            return 0
        dominant = max(dist, key=dist.get)
        return {"unripe": 7, "mid-ripe": 4, "ripe": 2}.get(dominant, 3)

    def to_dict(self) -> dict:
        return {
            "banana_type": self.banana_type,
            "total_samples": len(self),
            "average_length_cm": self.average_length(),
            "average_quality": self.average_quality(),
            "average_weight_g": self.average_weight(),
            "estimated_shelf_life_days": self.estimated_shelf_life_days(),
            "ripeness_distribution": self.ripeness_distribution(),
            "samples": [s.to_dict() for s in self.samples],
        }

    def __len__(self):
        return len(self.samples)

    def __iter__(self):
        return iter(self.samples)

    def __str__(self):
        return f"BananaBatch(type={self.banana_type}, samples={len(self)})"
