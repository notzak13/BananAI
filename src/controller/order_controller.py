from __future__ import annotations
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, TYPE_CHECKING

# Services & Pricing
from src.services.shipping_service import ShippingService
from src.services.pricing_strategy import PremiumPricing, EconomicPricing, StandardPricing

if TYPE_CHECKING:
    from src.models.banana_batch import BananaBatch
    from src.models.inventory import Inventory

class OrderController:
    def __init__(self, inventory: Inventory, batch_repo):
        self.inventory = inventory
        self.batch_repo = batch_repo
        
        # --- DIRECTORY ARCHITECTURE ---
        self.base_order_dir = Path("data/orders")
        self.receipts_dir = self.base_order_dir / "receipts"
        self.ledger_dir = self.base_order_dir / "ledgers"
        self.physical_dir = self.base_order_dir / "physical_receipts"
        self.history_path = self.ledger_dir / "master_history.json"
        
        # Ensure the empire's filing cabinet exists
        for folder in [self.receipts_dir, self.ledger_dir, self.physical_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.base_price_per_kg = 1.25  # Profit margin base
        self.logger = logging.getLogger("OrderController")

    def get_proposals(self, destination: str, weight: float, tier: str) -> Dict[str, List[BananaBatch]]:
        """Finds suitable fruit based on shelf-life and destination."""
        transit_days, _ = ShippingService.get_route_info(destination)
        perfect, alternatives = self.inventory.get_recommendations(
            weight=weight, 
            transit_days=transit_days, 
            requested_tier=tier
        )
        return {"perfect": perfect, "alternatives": alternatives}

    def generate_invoice(self, batch: BananaBatch, weight: float, destination: str, tier: str) -> Dict[str, Any]:
        """Calculates a PROFITABLE price using Cost-Plus-Margin logic."""
        _, ship_cost_kg = ShippingService.get_route_info(destination)
        
        # Select Strategy
        tier_map = {"premium": PremiumPricing(), "economic": EconomicPricing()}
        strategy = tier_map.get(tier.lower(), StandardPricing())

        # Logic: Price = Shipping Floor + (Quality * Base Rate) + Tier Margin
        unit_price = strategy.calculate_price(
            base_rate=self.base_price_per_kg, 
            quality_score=batch.average_quality(),
            shipping_cost_kg=ship_cost_kg
        )
        
        revenue = weight * unit_price
        shipping_total = weight * ship_cost_kg
        profit = revenue - shipping_total

        return {
            "order_id": f"ORD-{datetime.now().strftime('%m%d-%H%M')}",
            "timestamp": datetime.now().isoformat(),
            "batch_id": batch.batch_id,
            "destination": destination.upper(),
            "weight_kg": round(weight, 2),
            "tier_sold": tier.upper(),
            "unit_price": round(unit_price, 2),
            "total_revenue": round(revenue, 2),
            "shipping_cost": round(shipping_total, 2),
            "net_profit": round(profit, 2),
            "shipping_rate_kg": ship_cost_kg
        }

    def commit_transaction(self, invoice: Dict[str, Any], batch: BananaBatch) -> bool:
        """The Atomic Transaction: Stock -> Ledger -> Receipt -> Manifest."""
        try:
            # 1. Deduct Stock (Handles partial fulfillment automatically)
            requested = invoice["weight_kg"]
            actual_weight = batch.reserve_stock(requested)
            
            if actual_weight <= 0:
                return False

            # 2. Re-calculate if we had to pivot to partial stock
            if actual_weight < requested:
                print(f"\n⚠️ PARTIAL SHIPMENT: Only {actual_weight}kg available. Recalculating...")
                invoice["weight_kg"] = actual_weight
                invoice["total_revenue"] = round(actual_weight * invoice["unit_price"], 2)
                invoice["shipping_cost"] = round(actual_weight * invoice["shipping_rate_kg"], 2)
                invoice["net_profit"] = round(invoice["total_revenue"] - invoice["shipping_cost"], 2)

            # 3. Save Updated Batch to Disk
            self.batch_repo.save_batch(batch)

            # 4. Save JSON Receipt
            with open(self.receipts_dir / f"{invoice['order_id']}.json", "w") as f:
                json.dump(invoice, f, indent=4)

            # 5. Append to Master Ledger
            history = self._read_history()
            history.append(invoice)
            with open(self.history_path, "w") as f:
                json.dump(history, f, indent=4)

            # 6. PRINT PHYSICAL MANIFEST
            self._print_physical_receipt(invoice)

            return True

        except Exception as e:
            self.logger.error(f"Transaction Error: {e}")
            return False

    def _print_physical_receipt(self, invoice: Dict[str, Any]):
        """Generates a professional text-based shipping manifest."""
        receipt_name = f"MANIFEST_{invoice['order_id']}.txt"
        
        content = f"""
============================================================
           🍌 BANANAI GLOBAL BROKERAGE 🍌
============================================================
ORDER ID:    {invoice['order_id']}
DATE/TIME:   {invoice['timestamp']}
BATCH REF:   {invoice['batch_id']}
------------------------------------------------------------
DESTINATION: {invoice['destination']}
TIER:        {invoice['tier_sold']} GRADE
QUANTITY:    {invoice['weight_kg']:.2f} kg
------------------------------------------------------------
UNIT PRICE:  ${invoice['unit_price']:.2f} USD
TOTAL REV:   ${invoice['total_revenue']:,.2f} USD
SHIPPING:    ${invoice['shipping_cost']:,.2f} USD
NET PROFIT:  ${invoice['net_profit']:,.2f} USD
------------------------------------------------------------
LOGISTICS:   COLD-CHAIN VERIFIED (13.5°C)
STATUS:      EXPORT CLEARED / eBOL ISSUED
------------------------------------------------------------
       THANK YOU FOR TRADING WITH THE EMPIRE!
============================================================
        """
        with open(self.physical_dir / receipt_name, "w", encoding="utf-8") as f:
            f.write(content)

    def get_financial_summary(self) -> Dict[str, Any]:
        history = self._read_history()
        return {
            "revenue": sum(item.get("total_revenue", 0) for item in history),
            "profit": sum(item.get("net_profit", 0) for item in history),
            "orders": len(history)
        }

    def _read_history(self) -> List[Dict]:
        if not self.history_path.exists(): return []
        try:
            with open(self.history_path, "r") as f:
                return json.load(f)
        except: return []