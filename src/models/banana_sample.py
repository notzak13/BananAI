from typing import Dict, Any

class BananaSample:
    def __init__(self, banana: Any, timestamp: float = None):
        self.banana = banana  # This is your BananaObject from CV
        self.timestamp = timestamp

    def to_dict(self) -> Dict:
        return {
            "banana": self.banana.to_dict() if hasattr(self.banana, 'to_dict') else str(self.banana),
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BananaSample':
        """
        The missing link! 
        This allows the BatchRepository to rehydrate individual samples.
        """
        # We handle the 'banana' object differently depending on your CV setup
        # For now, we'll store the raw data back into the sample
        return cls(
            banana=data.get("banana"),
            timestamp=data.get("timestamp")
        )