import math

class StatisticsService:

    @staticmethod
    def describe(values: list[float]) -> dict:
        if not values:
            return {}

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance)

        return {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
        }

    @staticmethod
    def batch_statistics(batch) -> dict:
        lengths = [s.banana.length_cm for s in batch]
        weights = [s.banana.estimated_weight_g() for s in batch]
        qualities = [s.banana.quality_index() for s in batch]

        return {
            "length": StatisticsService.describe(lengths),
            "weight": StatisticsService.describe(weights),
            "quality": StatisticsService.describe(qualities),
        }
