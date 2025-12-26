import os
import shutil
from pathlib import Path

class InventoryManager:
    @staticmethod
    def archive_empty_batches(batches_dir: str = "data/batches", archive_dir: str = "data/archive"):
        """Moves depleted batches to an archive folder to keep the portal fast."""
        b_path = Path(batches_dir)
        a_path = Path(archive_dir)
        a_path.mkdir(parents=True, exist_ok=True)
        
        import json
        archived_count = 0
        
        for file in b_path.glob("*.json"):
            with open(file, "r") as f:
                data = json.load(f)
                if data.get("remaining_weight_kg", 0) <= 0:
                    shutil.move(str(file), str(a_path / file.name))
                    archived_count += 1
        
        return archived_count

    @staticmethod
    def get_restock_report(inventory):
        """Identifies which tiers are running low."""
        total_kg = inventory.get_total_stock_kg()
        report = []
        if total_kg < 1000:
            report.append("⚠️ CRITICAL: Total stock below 1,000kg!")
        if len(inventory.batches) < 3:
            report.append("📢 ALERT: Less than 3 active batches. Run CV pipeline.")
            
        return report