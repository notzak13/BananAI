class ShippingService:
    # Destination: (Days in transit, Cost per KG)
    # Calibrated for the 30-day "Unripe" shelf life
    ROUTES = {
        "USA": (5, 0.80),
        "GERMANY": (12, 2.10),
        "SPAIN": (10, 1.90),
        "CHINA": (18, 3.50),
        "LOCAL": (1, 0.20)
    }

    @staticmethod
    def get_route_info(destination: str):
        """Returns (transit_days, cost_per_kg) for a given destination."""
        return ShippingService.ROUTES.get(destination.upper(), (7, 1.50))

    @staticmethod
    def is_shipping_viable(shelf_life: int, transit_days: int) -> bool:
        """
        True if the banana survives the trip + 1 day buffer.
        If shelf_life is 0 (bug), this will always return False.
        """
        return shelf_life >= (transit_days + 1)