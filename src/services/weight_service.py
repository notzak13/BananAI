def estimate_weight_grams(length_cm: float) -> float:
    """
    Industrial heuristic for banana weight estimation (grams).
    """
    return round(2.8 * (length_cm ** 1.2), 2)
