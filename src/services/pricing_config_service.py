"""
Pricing Configuration Service for BananAI
Manages editable pricing for premium, standard, economic bananas, and shipping costs.
"""
import json
from pathlib import Path
from typing import Dict, Any

class PricingConfigService:
    """Manages pricing configuration with JSON storage."""
    
    DEFAULT_CONFIG = {
        "base_price_per_kg": 1.35,
        "premium": {
            "margin_multiplier": 1.50,
            "quality_bonus_multiplier": 1.5
        },
        "standard": {
            "margin_multiplier": 1.20,
            "quality_bonus_multiplier": 1.0
        },
        "economic": {
            "margin_multiplier": 1.05,
            "quality_bonus_multiplier": 0.5
        },
        "shipping": {
            "USA": 0.80,
            "GERMANY": 2.10,
            "SPAIN": 1.90,
            "CHINA": 3.50,
            "LOCAL": 0.20
        }
    }
    
    def __init__(self, config_file: Path = None):
        if config_file is None:
            config_file = Path("data/pricing_config.json")
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create default config if it doesn't exist."""
        if not self.config_file.exists():
            self._save_config(self.DEFAULT_CONFIG)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load pricing configuration."""
        if not self.config_file.exists():
            return self.DEFAULT_CONFIG.copy()
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = self.DEFAULT_CONFIG.copy()
                merged.update(config)
                if "shipping" in config:
                    merged["shipping"].update(config["shipping"])
                return merged
        except Exception:
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save pricing configuration."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def get_config(self) -> Dict[str, Any]:
        """Get current pricing configuration."""
        return self._load_config()
    
    def update_base_price(self, price: float):
        """Update base price per kg."""
        config = self._load_config()
        config["base_price_per_kg"] = price
        self._save_config(config)
    
    def update_tier_pricing(self, tier: str, margin_multiplier: float = None, 
                           quality_bonus_multiplier: float = None):
        """Update pricing for a specific tier (premium, standard, economic)."""
        config = self._load_config()
        tier_lower = tier.lower()
        
        if tier_lower not in ["premium", "standard", "economic"]:
            raise ValueError(f"Invalid tier: {tier}")
        
        if tier_lower not in config:
            config[tier_lower] = {}
        
        if margin_multiplier is not None:
            config[tier_lower]["margin_multiplier"] = margin_multiplier
        if quality_bonus_multiplier is not None:
            config[tier_lower]["quality_bonus_multiplier"] = quality_bonus_multiplier
        
        self._save_config(config)
    
    def update_shipping_cost(self, destination: str, cost_per_kg: float):
        """Update shipping cost for a destination."""
        config = self._load_config()
        if "shipping" not in config:
            config["shipping"] = {}
        config["shipping"][destination.upper()] = cost_per_kg
        self._save_config(config)
    
    def get_base_price(self) -> float:
        """Get base price per kg."""
        return self._load_config().get("base_price_per_kg", 1.35)
    
    def get_tier_config(self, tier: str) -> Dict[str, float]:
        """Get configuration for a specific tier."""
        config = self._load_config()
        return config.get(tier.lower(), {})
    
    def get_shipping_cost(self, destination: str) -> float:
        """Get shipping cost for a destination."""
        config = self._load_config()
        return config.get("shipping", {}).get(destination.upper(), 1.50)
