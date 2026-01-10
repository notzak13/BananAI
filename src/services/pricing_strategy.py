from abc import ABC, abstractmethod
from src.services.pricing_config_service import PricingConfigService

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        pass

class StandardPricing(PricingStrategy):
    def __init__(self, config_service: PricingConfigService = None):
        self.config_service = config_service or PricingConfigService()
    
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        config = self.config_service.get_tier_config("standard")
        margin = config.get("margin_multiplier", 1.20)
        quality_mult = config.get("quality_bonus_multiplier", 1.0)
        quality_bonus = base_rate * quality_score * quality_mult
        return round((shipping_cost_kg * margin) + quality_bonus, 2)

class PremiumPricing(PricingStrategy):
    def __init__(self, config_service: PricingConfigService = None):
        self.config_service = config_service or PricingConfigService()
    
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        config = self.config_service.get_tier_config("premium")
        margin = config.get("margin_multiplier", 1.50)
        quality_mult = config.get("quality_bonus_multiplier", 1.5)
        quality_bonus = (base_rate * quality_mult) * quality_score
        return round((shipping_cost_kg * margin) + quality_bonus, 2)

class EconomicPricing(PricingStrategy):
    def __init__(self, config_service: PricingConfigService = None):
        self.config_service = config_service or PricingConfigService()
    
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        config = self.config_service.get_tier_config("economic")
        margin = config.get("margin_multiplier", 1.05)
        quality_mult = config.get("quality_bonus_multiplier", 0.5)
        return round((shipping_cost_kg * margin) + (base_rate * quality_mult), 2)