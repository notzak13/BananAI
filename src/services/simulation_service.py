"""
Historical Sales Simulation Service
Generates simulated sales data between 2026-02-01 and 2028-02-01
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

class SimulationService:
    """Generates and manages simulated historical sales data."""
    
    DESTINATIONS = ["USA", "GERMANY", "SPAIN", "CHINA", "LOCAL"]
    TIERS = ["PREMIUM", "STANDARD", "ECONOMIC"]
    
    def __init__(self, history_path: Path = None):
        if history_path is None:
            history_path = Path("data/orders/ledgers/master_history.json")
        self.history_path = history_path
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load existing history."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_history(self, history: List[Dict[str, Any]]):
        """Save history to file."""
        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2)
    
    def _generate_simulated_order(self, timestamp: datetime, client_id: str = None) -> Dict[str, Any]:
        """Generate a single simulated order."""
        destination = random.choice(self.DESTINATIONS)
        tier = random.choice(self.TIERS)
        weight = random.uniform(100.0, 2000.0)
        
        # Simulate pricing based on tier
        base_price = 1.35
        shipping_rates = {
            "USA": 0.80, "GERMANY": 2.10, "SPAIN": 1.90, 
            "CHINA": 3.50, "LOCAL": 0.20
        }
        shipping_rate = shipping_rates.get(destination, 1.50)
        
        # Tier-based pricing multipliers
        tier_multipliers = {
            "PREMIUM": 1.50,
            "STANDARD": 1.20,
            "ECONOMIC": 1.05
        }
        quality_score = random.uniform(0.6, 0.95)
        unit_price = round((shipping_rate * tier_multipliers[tier]) + (base_price * quality_score), 2)
        
        total_revenue = round(weight * unit_price, 2)
        shipping_cost = round(weight * shipping_rate, 2)
        net_profit = round(total_revenue - shipping_cost, 2)
        
        # Generate batch_id
        batch_id = f"{random.randint(10000000, 99999999):x}"
        
        order = {
            "order_id": f"ORD-{timestamp.strftime('%m%d-%H%M')}-{random.randint(100, 999)}",
            "timestamp": timestamp.isoformat(),
            "batch_id": batch_id,
            "destination": destination,
            "weight_kg": round(weight, 2),
            "tier_sold": tier,
            "unit_price": unit_price,
            "total_revenue": total_revenue,
            "shipping_cost": shipping_cost,
            "net_profit": net_profit,
            "shipping_rate_kg": shipping_rate,
            "quality_at_sale": round(quality_score, 2),
            "simulated": True
        }
        
        if client_id:
            order["client_id"] = client_id
        
        return order
    
    def generate_historical_sales(self, num_orders: int = 100, 
                                 start_date: str = "2026-02-01",
                                 end_date: str = "2028-02-01",
                                 client_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate simulated historical sales.
        
        Args:
            num_orders: Number of orders to generate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            client_ids: Optional list of client IDs to assign to orders
        """
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        time_span = (end - start).total_seconds()
        
        simulated_orders = []
        
        for i in range(num_orders):
            # Random timestamp between start and end
            random_seconds = random.uniform(0, time_span)
            timestamp = start + timedelta(seconds=random_seconds)
            
            # Optionally assign to a client
            client_id = None
            if client_ids:
                client_id = random.choice(client_ids) if random.random() > 0.3 else None  # 70% have clients
            
            order = self._generate_simulated_order(timestamp, client_id)
            simulated_orders.append(order)
        
        # Sort by timestamp
        simulated_orders.sort(key=lambda x: x["timestamp"])
        
        return simulated_orders
    
    def add_simulated_sales_to_history(self, num_orders: int = 100,
                                      start_date: str = "2026-02-01",
                                      end_date: str = "2028-02-01",
                                      client_ids: List[str] = None,
                                      clear_existing: bool = False):
        """
        Add simulated sales to the master history.
        
        Args:
            num_orders: Number of orders to generate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            client_ids: Optional list of client IDs
            clear_existing: If True, clear existing simulated orders first
        """
        history = self._load_history()
        
        if clear_existing:
            # Remove only simulated orders, keep real ones
            history = [h for h in history if not h.get("simulated", False)]
        
        simulated = self.generate_historical_sales(num_orders, start_date, end_date, client_ids)
        history.extend(simulated)
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get("timestamp", ""))
        
        self._save_history(history)
        return len(simulated)
    
    def clear_simulated_sales(self):
        """Remove all simulated orders from history, keeping real ones."""
        history = self._load_history()
        original_count = len(history)
        history = [h for h in history if not h.get("simulated", False)]
        self._save_history(history)
        return original_count - len(history)
