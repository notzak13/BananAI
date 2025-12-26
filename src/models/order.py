from datetime import datetime

class Order:
    def __init__(self, destination: str, requested_weight: float, quality_tier: str):
        self.order_id = f"ORD-{int(datetime.now().timestamp())}"
        self.destination = destination
        self.requested_weight = requested_weight
        self.quality_tier = quality_tier # "premium", "standard", "economic"
        self.status = "PENDING"
        self.assigned_batch_id = None

    def get_min_quality_score(self) -> float:
        # Mapping tiers to your 0.0 - 1.0 quality index
        mapping = {
            "premium": 0.8,
            "standard": 0.5,
            "economic": 0.3
        }
        return mapping.get(self.quality_tier.lower(), 0.5)

    def get_transit_days(self) -> int:
        # Shipping logic from Ecuador
        routes = {
            "USA": 5,
            "Germany": 14,
            "Spain": 12,
            "China": 25,
            "Local": 2
        }
        return routes.get(self.destination, 10) # Default 10 days