import time

class BananaSample:
    def __init__(self, banana, timestamp=None):
        # banana can be the raw dict from detections
        self.banana = banana 
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        # If banana is an object, convert to dict, else keep as dict
        b_data = self.banana
        if hasattr(self.banana, 'to_dict'):
            b_data = self.banana.to_dict()
        elif hasattr(self.banana, '__dict__'):
            b_data = self.banana.__dict__
            
        return {
            "banana": b_data,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            banana=data.get("banana", {}),
            timestamp=data.get("timestamp")
        )