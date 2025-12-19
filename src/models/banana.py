from .fruit import Fruit
from src.services.weight_service import estimate_weight_grams


class Banana(Fruit):
    """
    Domain model representing a single banana.
    Uses physical heuristics and confidence-based quality scoring.
    """

    def __init__(
        self,
        length_cm: float,
        ripeness: str,
        confidence: float,
        mean_hsv: tuple
    ):
        super().__init__(confidence)

        if length_cm <= 0:
            raise ValueError("Length must be positive")

        self.length_cm = float(length_cm)
        self.ripeness = ripeness
        self.mean_hsv = mean_hsv

    # =========================
    # Physical estimation
    # =========================

    def estimated_weight_g(self) -> float:
        """
        Estimated weight in grams based on industrial heuristic.
        """
        return estimate_weight_grams(self.length_cm)

    def estimated_weight(self) -> float:
        """
        Alias for compatibility with older code.
        """
        return self.estimated_weight_g()

    # =========================
    # Quality model (OVERRIDE)
    # =========================

    def quality_index(self) -> float:
        """
        Quality score based on size, ripeness, and detection confidence.
        """
        size_factor = min(self.length_cm / 20.0, 1.0)

        ripeness_factor = {
            "unripe": 0.6,
            "mid-ripe": 1.0,
            "ripe": 0.8
        }.get(self.ripeness, 0.5)

        return round(size_factor * self._confidence * ripeness_factor, 2)

    # =========================
    # Dunder methods
    # =========================

    def __str__(self):
        return f"Banana({self.length_cm:.2f}cm, {self.ripeness})"

    def __eq__(self, other):
        return (
            isinstance(other, Banana)
            and abs(self.length_cm - other.length_cm) < 0.01
            and self.ripeness == other.ripeness
        )
