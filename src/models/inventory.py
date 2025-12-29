from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING
from src.services.shipping_service import ShippingService

if TYPE_CHECKING:
    from .banana_batch import BananaBatch

class Inventory:
    """
    High-level Controller for the Warehouse.
    Manages global stock and executes logistics matching algorithms.
    """
    def __init__(self):
        # Holds the live list of BananaBatch objects
        self.batches: List[BananaBatch] = []

    def add_batch(self, batch: BananaBatch):
        """
        Adds a batch to live memory. 
        Validation: Only tracks batches that actually have stock left.
        """
        if batch.remaining_weight_kg > 0:
            self.batches.append(batch)

    def get_recommendations(
        self, 
        weight: float, 
        transit_days: int, 
        requested_tier: str
    ) -> Tuple[List[BananaBatch], List[BananaBatch]]:
        """
        The 'Intelligence' of the system.
        Filters batches by:
        1. Shipping Viability (Can it survive the trip?)
        2. Quality Tier (Does it meet the customer's expectations?)
        """
        perfect_matches = []
        alternatives = []
        
        # 1. Tier Thresholding
        # Defines the minimum quality score required for each commercial tier
        req = requested_tier.lower()
        if req.startswith('p'): # Premium
            min_q = 0.65
        elif req.startswith('s'): # Standard
            min_q = 0.45
        else: # Economic
            min_q = 0.0

        for batch in self.batches:
            # --- LOGISTICS CORE ---
            # Extract real-time computed stats from the Batch object
            current_life = batch.estimated_shelf_life_days()
            avg_q = batch.average_quality()
            
            # Shipping viability is the #1 filter (Safety First: Don't ship rot)
            # This calls the ShippingService utility
            can_survive = ShippingService.is_shipping_viable(current_life, transit_days)
            
            if not can_survive:
                continue

            # --- MATCHING LOGIC ---
            # Perfect Match: Meets the quality tier requested
            quality_match = avg_q >= min_q
            
            if quality_match:
                perfect_matches.append(batch)
            else:
                # Alternative: Still sellable and survives shipping, 
                # but is a different quality grade
                alternatives.append(batch)

        # 2. PRO-LEVEL SORTING
        # Sort Perfect Matches: 
        # Primary: Quality (High to Low)
        # Secondary: Shelf Life (Freshness for long-distance hauls)
        perfect_matches.sort(
            key=lambda x: (x.average_quality(), x.estimated_shelf_life_days()), 
            reverse=True
        )
        
        # Sort Alternatives:
        # Prioritize Quality so the user sees the 'Next Best Thing'
        alternatives.sort(key=lambda x: x.average_quality(), reverse=True)

        return perfect_matches, alternatives

    def get_total_stock_kg(self) -> float:
        """
        Financial Intelligence: 
        Aggregates all remaining mass across all batches in the system.
        """
        return sum(b.remaining_weight_kg for b in self.batches)

    def find_batch_by_id(self, batch_id: str) -> Optional[BananaBatch]:
        """Utility for targeted inventory operations."""
        for b in self.batches:
            if b.batch_id == batch_id:
                return b
        return None