import cv2
import numpy as np

def analyze_color(frame, mask):
    # 1. Validation: Ensure mask is valid and contains data
    if mask is None or np.sum(mask) == 0:
        return {"ripeness": "unknown", "hue": 0, "saturation": 0}

    # 2. Convert to HSV once
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 3. Extract pixels where mask is true
    # We use the mask directly as an index to avoid slicing errors
    pixels = hsv[mask > 0]
    
    if len(pixels) == 0:
        return {"ripeness": "unknown", "hue": 0, "saturation": 0}

    # 4. Calculate Mean Stats
    mean_hsv = pixels.mean(axis=0)
    h = mean_hsv[0] # Hue
    s = mean_hsv[1] # Saturation

    # 5. Top Tier Calibration (OpenCV HSV: H is 0-180)
    # Green (Unripe): Hue ~35-90
    # Yellow (Mid-ripe): Hue ~22-34
    # Brown/Deep Yellow (Ripe): Hue < 22
    if h > 35:
        ripeness = "unripe"
    elif h > 22:
        ripeness = "mid-ripe"
    else:
        ripeness = "ripe"

    return {
        "ripeness": ripeness, 
        "hue": round(float(h), 2), 
        "saturation": round(float(s), 2),
        "mean_hsv": mean_hsv.tolist()
    }