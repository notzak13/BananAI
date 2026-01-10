import os
import shutil
import json
from pathlib import Path
# FIXED: Absolute import from the project root
from src.models.banana_batch import BananaBatch

class InventoryManager:
    @staticmethod
    def archive_empty_batches(batches_dir: str = "data/batches", archive_dir: str = "data/archive"):
        """Moves depleted batches to an archive folder to keep the UI clean."""
        b_path = Path(batches_dir)
        a_path = Path(archive_dir)
        a_path.mkdir(parents=True, exist_ok=True)
        
        archived_count = 0
        for file in b_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    # Archive if 0kg left or if marked as depleted
                    if data.get("remaining_weight_kg", 0) <= 0:
                        shutil.move(str(file), str(a_path / file.name))
                        archived_count += 1
            except Exception:
                continue
        return archived_count

    @staticmethod
    def reset_all_sales_and_shipments(history_file: str = "data/order_history.json"):
        """
        THE NUCLEAR RESET:
        Wipes the ledger and shipment history while preserving physical inventory.
        """
        h_path = Path(history_file)
        try:
            # We overwrite with an empty list [] so the JSON remains valid for the app
            with open(h_path, "w") as f:
                json.dump([], f, indent=2)
            return True, "Imperial Ledger has been wiped. Revenue reset to $0.00."
        except Exception as e:
            return False, f"Failed to reset ledger: {str(e)}"

    @staticmethod
    def get_restock_report(inventory):
        """Identifies which tiers are running low based on warehouse levels."""
        total_kg = inventory.get_total_stock_kg()
        report = []
        if total_kg < 1000:
            report.append("⚠️  CRITICAL: Warehouse total below 1,000kg!")
        if len(inventory.batches) < 3:
            report.append("📢  ALERT: Limited batch diversity. Resupply needed.")
        return report