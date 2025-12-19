from .banana import Banana


class BananaSample:
    def __init__(self, banana: Banana, timestamp: float):
        self.banana = banana
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "length_cm": self.banana.length_cm,
            "ripeness": self.banana.ripeness,
            "confidence": self.banana._confidence,
            "quality_index": self.banana.quality_index(),
            "estimated_weight_g": self.banana.estimated_weight(),
            "timestamp": self.timestamp,
        }
