def estimate_shelf_life(ripeness: str) -> int:
    """Professional Logistics Shelf-Life Mapping."""
    return {
        "unripe": 21,    # High export potential
        "mid-ripe": 10,  # Regional transit
        "ripe": 4        # Immediate local consumption
    }.get(ripeness, 0)

def quality_score(length: float, confidence: float, ripeness: str) -> float:
    """
    Re-calibrated for real-world variance (0.26 - 0.74 range).
    """
    # Base from AI Confidence
    score = (confidence or 0.8) * 0.3 

    # 1. Size Grade (Adjusted thresholds)
    if length > 20:       # Big bananas
        score += 0.30
    elif length >= 14:    # Standard bananas
        score += 0.15
    else:                 # Small/Discard
        score -= 0.05

    # 2. Logistics Value
    if ripeness == "unripe":
        score += 0.20
    elif ripeness == "mid-ripe":
        score += 0.10
    else:
        score += 0.05

    return round(max(0.1, min(score, 1.0)), 2)