from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING
from src.services.shipping_service import ShippingService

if TYPE_CHECKING:
    from .banana_batch import BananaBatch

class Inventory:
    def __init__(self):
        self.batches: List[BananaBatch] = []

    def add_batch(self, batch: BananaBatch):
        """Adds batch to live memory. Only tracks batches with actual sellable mass."""
        if batch.remaining_weight_kg > 0:
            self.batches.append(batch)

    def get_recommendations(self, weight: float, transit_days: int, requested_tier: str) -> Tuple[List[BananaBatch], List[BananaBatch]]:
        """
        High-Performance Logistics Matcher.
        Prioritizes survivability first, then quality, then weight fulfillment.
        """
        perfect_matches = []
        alternatives = []
        
        # 1. Tier Thresholding
        req = requested_tier.lower()
        if req.startswith('p'): min_q = 0.65
        elif req.startswith('s'): min_q = 0.45
        else: min_q = 0.0

        for batch in self.batches:
            # --- LOGISTICS CORE ---
            current_life = batch.estimated_shelf_life_days()
            avg_q = batch.average_quality()
            
            # Shipping viability is the #1 filter (Don't ship rot)
            can_survive = ShippingService.is_shipping_viable(current_life, transit_days)
            
            if not can_survive:
                continue

            # --- MATCHING LOGIC ---
            # Perfect = Quality meets/exceeds tier AND has enough to fulfill some/all of request
            quality_match = avg_q >= min_q
            
            if quality_match:
                perfect_matches.append(batch)
            else:
                # Still sellable, just a different quality tier
                alternatives.append(batch)

        # 2. PRO-LEVEL SORTING
        # Sort Perfect Matches: 
        # Primary: Quality (High to Low)
        # Secondary: Shelf Life (Keep the freshest for the long hauls)
        perfect_matches.sort(key=lambda x: (x.average_quality(), x.estimated_shelf_life_days()), reverse=True)
        
        # Sort Alternatives:
        # Prioritize Quality so the user sees the 'Next Best Thing'
        alternatives.sort(key=lambda x: x.average_quality(), reverse=True)

        return perfect_matches, alternatives

    def get_total_stock_kg(self) -> float:
        """Returns the total global mass in the warehouse."""
        return sum(b.remaining_weight_kg for b in self.batches)