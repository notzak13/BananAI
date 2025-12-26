from .fruit import Fruit
from src.services.weight_service import estimate_weight_grams

class Banana(Fruit):
    def __init__(self, length_cm, ripeness, confidence, mean_hsv=(0, 0, 0)):
        # Fruit class usually takes (confidence, name)
        super().__init__(confidence)

        if length_cm <= 0:
            # Fallback for corrupted data during load
            self.length_cm = 15.0 
        else:
            self.length_cm = float(length_cm)
            
        self.ripeness = ripeness if ripeness else "unknown"
        self.confidence = float(confidence)
        self.mean_hsv = mean_hsv

    # --- Logistics Quality Model (The Brain) ---

    def quality_index(self) -> float:
        """
        High-precision quality scoring calibrated to 0.26 - 0.74 real-world data.
        This score determines if the batch is 'Premium' (0.65+).
        """
        # 1. Base Score from AI Confidence (30% weight)
        score = (self._confidence or 0.8) * 0.30

        # 2. Size Multiplier (The 'Export Grade' factor)
        # 22cm+ is the gold standard for top-tier logistics
        if self.length_cm > 22:
            score += 0.40
        elif self.length_cm >= 15:
            score += 0.20
        else:
            score -= 0.05 # Under-sized penalty

        # 3. Ripeness Value (Logistics Green-Life)
        # Unripe has the highest value for long-distance shipping
        ripeness_map = {
            "unripe": 0.30,    # 30 days life
            "mid-ripe": 0.15,  # 14 days life
            "ripe": 0.05       # 7 days life
        }
        score += ripeness_map.get(self.ripeness, 0.10)

        # 4. Normalization (Clamp between 0.1 and 1.0)
        return round(max(0.1, min(score, 1.0)), 2)

    # --- Physical Estimation ---

    def estimated_weight_g(self) -> float:
        return estimate_weight_grams(self.length_cm)

    def estimated_weight(self) -> float:
        return self.estimated_weight_g()

    # --- Data Serialization (Fixes the "Life: 0" Bug) ---

    def to_dict(self) -> dict:
        return {
            "length_cm": self.length_cm,
            "ripeness": self.ripeness,
            "confidence": self._confidence,
            "mean_hsv": self.mean_hsv,
            "quality_index": self.quality_index()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Banana':
        return cls(
            length_cm=data.get("length_cm", 0),
            ripeness=data.get("ripeness", "unknown"),
            confidence=data.get("confidence", 0),
            mean_hsv=data.get("mean_hsv", (0, 0, 0))
        )

    # --- Dunder methods ---

    def __str__(self):
        return f"Banana({self.length_cm:.2f}cm, {self.ripeness}, Q:{self.quality_index()})"

    def __eq__(self, other):
        return (
            isinstance(other, Banana)
            and abs(self.length_cm - other.length_cm) < 0.01
            and self.ripeness == other.ripeness
        )