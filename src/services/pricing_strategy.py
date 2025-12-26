from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        pass

class StandardPricing(PricingStrategy):
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        # Floor price = Shipping + 20% margin
        # Add quality bonus on top
        margin = 1.20 
        quality_bonus = base_rate * quality_score
        return round((shipping_cost_kg * margin) + quality_bonus, 2)

class PremiumPricing(PricingStrategy):
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        # Floor price = Shipping + 50% margin
        margin = 1.50
        quality_bonus = (base_rate * 1.5) * quality_score
        return round((shipping_cost_kg * margin) + quality_bonus, 2)

class EconomicPricing(PricingStrategy):
    def calculate_price(self, base_rate: float, quality_score: float, shipping_cost_kg: float) -> float:
        # Floor price = Shipping + 5% margin (Quick liquidation)
        margin = 1.05
        return round((shipping_cost_kg * margin) + (base_rate * 0.5), 2)