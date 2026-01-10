import uuid
import time
from typing import List, Dict, Optional, Any
# Ensure this import matches your project structure
from .banana_sample import BananaSample

class BananaBatch:
    """
    The Core Engine of the BananaI Empire.
    Handles telemetry extraction, stock depletion, and serialization.
    """
    def __init__(self, banana_type: str, batch_id: str = None, 
                 total_weight_kg: float = 0.0, received_date: float = None):
        self.batch_id = batch_id or str(uuid.uuid4())[:8]
        self.banana_type = banana_type
        self.received_date = received_date or time.time()
        self.total_weight_kg = float(total_weight_kg)
        self.remaining_weight_kg = float(total_weight_kg)
        self.samples: List[BananaSample] = []
        
        # Runtime Cache - prevents heavy recalculation on every UI render
        self._cached_quality = None
        self._cached_life = None

    # --- INVENTORY LOGIC ---

    def reserve_stock(self, amount_kg: float) -> bool:
        """
        Attempts to deplete stock. 
        Returns True if successful, False if insufficient.
        """
        if amount_kg <= 0:
            return False
        if amount_kg <= self.remaining_weight_kg:
            self.remaining_weight_kg = round(self.remaining_weight_kg - amount_kg, 2)
            return True
        return False

    @property
    def status(self) -> str:
        """Quick status for the terminal UI."""
        if self.remaining_weight_kg <= 0: return "DEPLETED"
        if self.remaining_weight_kg < (self.total_weight_kg * 0.1): return "CRITICAL"
        return "HEALTHY"

    # --- TELEMETRY EXTRACTION ---

    def add_sample(self, sample: BananaSample):
        """Ingests new CV data and invalidates the cache."""
        self.samples.append(sample)
        self._cached_quality = None
        self._cached_life = None

    def _extract(self, obj, keys: List[str]):
        """Indestructible extractor for dicts, objects, or methods."""
        for key in keys:
            # Case 1: Dict access
            if isinstance(obj, dict):
                val = obj.get(key)
                if val is not None: return val
            # Case 2: Object attribute or method
            elif hasattr(obj, key):
                attr = getattr(obj, key)
                return attr() if callable(attr) else attr
        return None

    def average_quality(self) -> float:
        """Calculates mean quality across all visual samples."""
        if self._cached_quality is not None: return self._cached_quality
        if not self.samples: return 0.0

        scores = []
        for s in self.samples:
            # Maps multiple possible key names from various CV pipeline versions
            val = self._extract(s.banana, ['quality_index', 'quality_score', 'quality'])
            if val is not None:
                scores.append(float(val))

        self._cached_quality = round(sum(scores) / len(scores), 2) if scores else 0.0
        return self._cached_quality

    def estimated_shelf_life_days(self) -> int:
        """
        Calculates the shelf life.
        PRIORITY: 1. Locked JSON Value > 2. Sample Extraction > 3. Fallback
        """
        # If we loaded from JSON, this will be set. We MUST trust it.
        if self._cached_life is not None:
            return int(self._cached_life)
            
        # If no cache, try to calculate from samples
        lives = []
        for s in self.samples:
            source = s.banana if hasattr(s, 'banana') else s.get('banana', {})
            val = self._extract(source, ['shelf_life_days', 'days_left'])
            if val is not None:
                lives.append(int(val))
        
        if lives:
            self._cached_life = min(lives)
            return int(self._cached_life)

        return 7 # Absolute floor if JSON and Samples are both missing data

    @classmethod
    def from_dict(cls, data: dict) -> 'BananaBatch':
        """
        REHYDRATION ENGINE: This is where we force the object to 
        accept the JSON's real values.
        """
        batch = cls(
            banana_type=data.get("banana_type", "Cavendish"),
            batch_id=data.get("batch_id"),
            total_weight_kg=float(data.get("total_weight_kg", 0.0)),
            received_date=data.get("received_date")
        )
        batch.remaining_weight_kg = float(data.get("remaining_weight_kg", batch.total_weight_kg))
        
        # --- THE MASTER FIX ---
        # Look specifically at the 'computed_stats' block in your JSON
        stats = data.get("computed_stats", {})
        
        # We LOCK these values into the cache immediately.
        # This prevents the 'ripeness mapping' from ever running.
        if "shelf_life_days" in stats:
            batch._cached_life = int(stats["shelf_life_days"])
        
        if "avg_quality" in stats:
            batch._cached_quality = float(stats["avg_quality"])

        # Reconstruct samples
        if "samples" in data:
            from .banana_sample import BananaSample
            for s_data in data["samples"]:
                try:
                    batch.samples.append(BananaSample.from_dict(s_data))
                except:
                    batch.samples.append(s_data)
                    
        return batch
    
    # --- SERIALIZATION ---

    def to_dict(self) -> dict:
        """Converts object to JSON-ready dictionary."""
        return {
            "batch_id": self.batch_id,
            "banana_type": self.banana_type,
            "received_date": self.received_date,
            "total_weight_kg": self.total_weight_kg,
            "remaining_weight_kg": self.remaining_weight_kg,
            "status": self.status,
            "computed_stats": {
                "avg_quality": self.average_quality(),
                "shelf_life_days": self.estimated_shelf_life_days()
            },
            "samples": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.samples]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BananaBatch':
        """Reconstructs the object from disk data."""
        batch = cls(
            banana_type=data.get("banana_type", "Cavendish"),
            batch_id=data.get("batch_id"),
            total_weight_kg=float(data.get("total_weight_kg", 0.0)),
            received_date=data.get("received_date")
        )
        batch.remaining_weight_kg = float(data.get("remaining_weight_kg", batch.total_weight_kg))
        
        if "samples" in data:
            for s_data in data["samples"]:
                # Logic assumes BananaSample has a from_dict method
                batch.samples.append(BananaSample.from_dict(s_data))
        return batch