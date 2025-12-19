def estimate_shelf_life(ripeness):
    return {
        "green": 10,
        "ripe": 5,
        "overripe": 2
    }.get(ripeness, 0)


def quality_score(length, confidence, ripeness):
    score = confidence * 0.6

    if length > 15:
        score += 0.2
    if ripeness == "ripe":
        score += 0.2

    return round(min(score, 1.0), 2)
