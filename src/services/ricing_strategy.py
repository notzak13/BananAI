from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_price: float, quality_score: float) -> float:
        pass

class PremiumPricing(PricingStrategy):
    def calculate_price(self, base_price, quality_score):
        # Premium adds a 50% markup + a bonus for exceptionally high quality scores
        quality_bonus = (quality_score - 0.8) * 2 if quality_score > 0.8 else 0
        return base_price * 1.5 + quality_bonus

class EconomicPricing(PricingStrategy):
    def calculate_price(self, base_price, quality_score):
        # Economic offers a 20% discount but stays above cost
        return base_price * 0.8