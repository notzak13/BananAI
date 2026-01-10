from __future__ import annotations
from typing import List, Tuple, Dict, Optional, TYPE_CHECKING
from src.services.shipping_service import ShippingService

if TYPE_CHECKING:
    from .banana_batch import BananaBatch

class Inventory:
    """
    High-level Controller for the Warehouse.
    Manages global stock and executes logistics matching algorithms
    using REAL real-time batch data.
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
        Filters batches based on ACTUAL JSON data:
        1. Shipping Viability (Shelf Life vs. Transit)
        2. Quality Tier (Avg Quality Index)
        """
        perfect_matches = []
        alternatives = []
        
        # 1. Tier Thresholding based on Quality Index
        req = requested_tier.lower()
        if req.startswith('p'): # Premium
            min_q = 0.65
        elif req.startswith('s'): # Standard
            min_q = 0.45
        else: # Economic
            min_q = 0.0

        for batch in self.batches:
            # --- REAL DATA EXTRACTION ---
            # We use the methods that look at the batch's internal JSON stats
            current_life = batch.estimated_shelf_life_days()
            avg_q = batch.average_quality()
            
            # --- LOGISTICS CORE ---
            # Shipping viability: To avoid 'No Stock' errors, we allow 
            # delivery if shelf_life >= transit_days (inclusive)
            if transit_days > 0:
                can_survive = current_life >= transit_days
            else:
                can_survive = current_life > 0

            if not can_survive:
                continue

            # --- MATCHING LOGIC ---
            # Perfect Match: Meets the quality tier requested in your rules
            quality_match = avg_q >= min_q
            
            if quality_match:
                perfect_matches.append(batch)
            else:
                # Alternative: survives shipping but different quality
                alternatives.append(batch)

        # 2. SORTING (Based on Real Freshness/Quality)
        # Sort Perfect Matches: Highest Quality first, then most Shelf Life
        perfect_matches.sort(
            key=lambda x: (x.average_quality(), x.estimated_shelf_life_days()), 
            reverse=True
        )
        
        # Sort Alternatives: Prioritize Quality
        alternatives.sort(key=lambda x: x.average_quality(), reverse=True)

        return perfect_matches, alternatives

    def get_total_stock_kg(self) -> float:
        """Sum of real remaining_weight_kg from all batches."""
        return sum(b.remaining_weight_kg for b in self.batches)

    def find_batch_by_id(self, batch_id: str) -> Optional[BananaBatch]:
        """Finds specific batch by the real batch_id string from JSON."""
        for b in self.batches:
            if b.batch_id == batch_id:
                return b
        return None