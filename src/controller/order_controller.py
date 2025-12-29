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
    """
    The Command & Control Hub for transactions.
    Orchestrates inventory depletion, financial calculations, and legal manifest generation.
    """
    def __init__(self, inventory: Inventory, batch_repo):
        self.inventory = inventory
        self.batch_repo = batch_repo
        
        # --- DIRECTORY ARCHITECTURE ---
        self.base_order_dir = Path("data/orders")
        self.receipts_dir = self.base_order_dir / "receipts"
        self.ledger_dir = self.base_order_dir / "ledgers"
        self.physical_dir = self.base_order_dir / "physical_receipts"
        self.history_path = self.ledger_dir / "master_history.json"
        
        # Ensure the infrastructure exists
        for folder in [self.receipts_dir, self.ledger_dir, self.physical_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.base_price_per_kg = 1.35  # Adjusted for market inflation
        self.logger = logging.getLogger("OrderController")

    def get_proposals(self, destination: str, weight: float, tier: str) -> Dict[str, List[BananaBatch]]:
        """Matches destination transit requirements against batch shelf-life."""
        transit_days, _ = ShippingService.get_route_info(destination)
        
        # Pull from inventory using refined logistics logic
        perfect, alternatives = self.inventory.get_recommendations(
            weight=weight, 
            transit_days=transit_days, 
            requested_tier=tier
        )
        return {"perfect": perfect, "alternatives": alternatives}

    def generate_invoice(self, batch: BananaBatch, weight: float, destination: str, tier: str) -> Dict[str, Any]:
        """Calculates dynamic pricing based on shipping floor + quality margin."""
        _, ship_cost_kg = ShippingService.get_route_info(destination)
        
        # Strategy Pattern for Dynamic Pricing
        tier_map = {
            "premium": PremiumPricing(), 
            "economic": EconomicPricing(),
            "standard": StandardPricing()
        }
        strategy = tier_map.get(tier.lower(), StandardPricing())

        # Logic: (Base * Quality) + Tier Margin + Shipping Cost
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
            "shipping_rate_kg": ship_cost_kg,
            "quality_at_sale": batch.average_quality()
        }

    def commit_transaction(self, invoice: Dict[str, Any], batch: BananaBatch) -> bool:
        """
        The Atomic Transaction. 
        Updates: Stock Object -> JSON Batch File -> Ledger -> Physical TXT Manifest.
        """
        try:
            requested = invoice["weight_kg"]
            
            # 1. Attempt Stock Depletion
            # Check if Batch has the method (we just added it to BananaBatch)
            if not batch.reserve_stock(requested):
                # Check for partial fulfillment if requested > remaining
                if batch.remaining_weight_kg > 0:
                    actual_weight = batch.remaining_weight_kg
                    batch.reserve_stock(actual_weight) # Take what's left
                    
                    # 2. Recalculate Invoice for Partial Shipment
                    print(f"\n[LOGISTICS] PIVOT: Only {actual_weight}kg available. Adjusting Manifest...")
                    invoice["weight_kg"] = actual_weight
                    invoice["total_revenue"] = round(actual_weight * invoice["unit_price"], 2)
                    invoice["shipping_cost"] = round(actual_weight * invoice["shipping_rate_kg"], 2)
                    invoice["net_profit"] = round(invoice["total_revenue"] - invoice["shipping_cost"], 2)
                else:
                    return False

            # 3. Persistence: Write Batch Change to Disk
            # If this fails, we haven't written the receipt yet, keeping it clean
            self.batch_repo.save_batch(batch)

            # 4. Save Digital JSON Receipt
            receipt_file = self.receipts_dir / f"{invoice['order_id']}.json"
            with open(receipt_file, "w") as f:
                json.dump(invoice, f, indent=4)

            # 5. Global Ledger Update (Master History)
            history = self._read_history()
            history.append(invoice)
            with open(self.history_path, "w") as f:
                json.dump(history, f, indent=4)

            # 6. Physical Manifest Generation (for the eBOL folder)
            self._print_physical_receipt(invoice)

            return True

        except Exception as e:
            self.logger.error(f"🛑 CRITICAL TRANSACTION FAILURE: {e}")
            return False

    def _print_physical_receipt(self, invoice: Dict[str, Any]):
        """Generates a high-fidelity text-based Bill of Lading."""
        receipt_name = f"MANIFEST_{invoice['order_id']}.txt"
        
        # Building the manifest with "BananaI" branding
        content = (
            "============================================================\n"
            "               🍌 BANANAI GLOBAL BROKERAGE 🍌               \n"
            "            Official Bill of Lading & Manifest              \n"
            "============================================================\n"
            f"ORDER ID:    {invoice['order_id']}\n"
            f"TIMESTAMP:   {invoice['timestamp']}\n"
            f"BATCH REF:   {invoice['batch_id']}\n"
            "------------------------------------------------------------\n"
            f"DESTINATION: {invoice['destination']}\n"
            f"GRADE:       {invoice['tier_sold']}\n"
            f"NET WEIGHT:  {invoice['weight_kg']:.2f} kg\n"
            "------------------------------------------------------------\n"
            f"UNIT PRICE:  ${invoice['unit_price']:.2f} USD/kg\n"
            f"SUBTOTAL:    ${invoice['total_revenue']:,.2f} USD\n"
            f"LOGISTICS:   ${invoice['shipping_cost']:,.2f} USD\n"
            f"NET PROFIT:  ${invoice['net_profit']:,.2f} USD\n"
            "------------------------------------------------------------\n"
            "ROUTE:       COLD-CHAIN SECURE / SEALED\n"
            "QUALITY:     VERIFIED BY COMPUTER VISION AI\n"
            "------------------------------------------------------------\n"
            "       THANK YOU FOR TRADING WITH THE EMPIRE!               \n"
            "============================================================\n"
        )
        
        try:
            with open(self.physical_dir / receipt_name, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            self.logger.warning(f"Failed to print physical manifest: {e}")

    def get_financial_summary(self) -> Dict[str, Any]:
        """Aggregates all-time financial performance."""
        history = self._read_history()
        return {
            "revenue": sum(item.get("total_revenue", 0) for item in history),
            "profit": sum(item.get("net_profit", 0) for item in history),
            "orders": len(history)
        }

    def _read_history(self) -> List[Dict]:
        """Safe read of the master ledger."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []