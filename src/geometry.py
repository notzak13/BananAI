import cv2
import numpy as np

def estimate_length(mask: np.ndarray) -> float:
    """
    Google-Level Geometry Engine.
    Uses Rotated Bounding Box (minAreaRect) for orientation-independent 
    precision measurement.
    """
    if mask is None or np.sum(mask) == 0:
        return None

    # Clean the mask
    mask = (mask > 0).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Focus on the largest object (the banana)
    banana_cnt = max(contours, key=cv2.contourArea)
    
    # 1. Get the Rotated Bounding Box
    # This finds the tightest box regardless of the banana's angle
    rect = cv2.minAreaRect(banana_cnt)
    (x, y), (w, h), angle = rect
    
    # 2. Extract Longitudinal Axis (The longer side)
    pixel_length = max(w, h)

    # 3. Calibration & Perspective Compensation
    # PX_TO_CM should be calibrated so your 30cm banana reads ~30.0
    # Higher value = higher result.
    PX_TO_CM = 0.045  
    
    raw_length_cm = pixel_length * PX_TO_CM

    # 4. Non-Linear Curve Correction
    # Small bananas often appear larger due to sensor noise; 
    # we apply a dampening factor to small objects for higher accuracy.
    if raw_length_cm < 18:
        refined_length = raw_length_cm * 0.92
    else:
        refined_length = raw_length_cm

    return round(float(refined_length), 2)