from src.services.pricing_config_service import PricingConfigService

class ShippingService:
    # Destination: (Days in transit, Cost per KG)
    # Calibrated for the 30-day "Unripe" shelf life
    ROUTES_DAYS = {
        "USA": 5,
        "GERMANY": 12,
        "SPAIN": 10,
        "CHINA": 18,
        "LOCAL": 1
    }

    def __init__(self, config_service: PricingConfigService = None):
        self.config_service = config_service or PricingConfigService()

    @staticmethod
    def get_route_info(destination: str, config_service: PricingConfigService = None):
        """Returns (transit_days, cost_per_kg) for a given destination."""
        transit_days = ShippingService.ROUTES_DAYS.get(destination.upper(), 7)
        
        if config_service:
            cost_per_kg = config_service.get_shipping_cost(destination)
        else:
            # Fallback to default if no config service
            default_costs = {
                "USA": 0.80,
                "GERMANY": 2.10,
                "SPAIN": 1.90,
                "CHINA": 3.50,
                "LOCAL": 0.20
            }
            cost_per_kg = default_costs.get(destination.upper(), 1.50)
        
        return transit_days, cost_per_kg

    @staticmethod
    def is_shipping_viable(shelf_life: int, transit_days: int) -> bool:
        """
        True if the banana survives the trip + 1 day buffer.
        If shelf_life is 0 (bug), this will always return False.
        """
        return shelf_life >= (transit_days + 1)