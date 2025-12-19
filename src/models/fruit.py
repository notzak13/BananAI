from abc import ABC, abstractmethod

class Fruit(ABC):
    def __init__(self, confidence: float):
        self._confidence = confidence

    @abstractmethod
    def quality_index(self) -> float:
        pass
