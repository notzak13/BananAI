import cv2
import numpy as np

# Empirical scale: px → cm
# Tuned once using a ruler, then fixed
PX_TO_CM = 0.035   # ← THIS is the key


def estimate_length(mask):
    mask = (mask > 0).astype(np.uint8) * 255

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    if not contours:
        return None

    banana = max(contours, key=cv2.contourArea)

    # Curved arc length
    length_px = cv2.arcLength(banana, closed=False)

    # Empirical correction (curve overcount)
    length_px *= 0.55

    length_cm = length_px * PX_TO_CM

    # Biological sanity clamp
    if length_cm < 10 or length_cm > 30:
        return None

    return round(length_cm, 2)
