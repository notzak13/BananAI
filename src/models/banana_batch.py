import uuid
import time
from typing import List, Dict, Optional, Any
from .banana_sample import BananaSample

class BananaBatch:
    def __init__(
        self, 
        banana_type: str, 
        batch_id: str = None, 
        total_weight_kg: float = 0.0,
        received_date: float = None
    ):
        self.batch_id = batch_id or str(uuid.uuid4())[:8]
        self.banana_type = banana_type
        self.received_date = received_date or time.time()
        self.total_weight_kg = float(total_weight_kg)
        self.remaining_weight_kg = float(total_weight_kg)
        self.samples: List[BananaSample] = []
        
        # New: Cached stats from JSON
        self._cached_quality = None
        self._cached_life = None

    def average_quality(self) -> float:
        # 1. Use cached value from JSON if available
        if self._cached_quality is not None:
            return self._cached_quality
        
        # 2. Otherwise calculate from samples
        if not self.samples: return 0.5
        vals = []
        for s in self.samples:
            if isinstance(s.banana, dict):
                # Check every possible key name CV might have used
                q = s.banana.get('quality_index') or s.banana.get('quality_score') or 0.5
                vals.append(float(q))
        return round(sum(vals) / len(vals), 2) if vals else 0.5

    def estimated_shelf_life_days(self) -> int:
        if self._cached_life is not None:
            return self._cached_life
            
        if not self.samples: return 30
        
        # Logic to extract ripeness from diverse sample formats
        ripeness_list = []
        for s in self.samples:
            if isinstance(s.banana, dict):
                ripeness_list.append(s.banana.get('ripeness', 'unripe'))
        
        if not ripeness_list: return 30
        dominant = max(set(ripeness_list), key=ripeness_list.count)
        return {"unripe": 30, "mid-ripe": 14, "ripe": 7}.get(dominant, 5)

    def reserve_stock(self, amount_kg: float) -> float:
        requested = round(float(amount_kg), 2)
        available = round(float(self.remaining_weight_kg), 2)
        if available <= 0: return 0.0
        if available >= requested:
            self.remaining_weight_kg = round(available - requested, 2)
            return requested
        actual_taken = available
        self.remaining_weight_kg = 0.0
        return actual_taken

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "banana_type": self.banana_type,
            "received_date": self.received_date,
            "total_weight_kg": self.total_weight_kg,
            "remaining_weight_kg": self.remaining_weight_kg,
            "computed_stats": {
                "avg_quality": self.average_quality(),
                "shelf_life_days": self.estimated_shelf_life_days()
            },
            "samples": [s.to_dict() for s in self.samples]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BananaBatch':
        batch = cls(
            banana_type=data.get("banana_type", "Cavendish"),
            batch_id=data.get("batch_id"),
            total_weight_kg=float(data.get("total_weight_kg", 0.0)),
            received_date=data.get("received_date")
        )
        batch.remaining_weight_kg = float(data.get("remaining_weight_kg", batch.total_weight_kg))
        
        # LOAD CACHED STATS: This is the fix!
        stats = data.get("computed_stats", {})
        batch._cached_quality = stats.get("avg_quality")
        batch._cached_life = stats.get("shelf_life_days")
        
        if "samples" in data:
            from .banana_sample import BananaSample
            for s_data in data["samples"]:
                batch.samples.append(BananaSample.from_dict(s_data))
        return batch