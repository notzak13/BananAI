import cv2

def analyze_color(image, mask):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mean_hsv = hsv[mask].mean(axis=0)

    h = mean_hsv[0]

    if h < 35:
        ripeness = "unripe"
    elif h < 50:
        ripeness = "mid-ripe"
    elif h < 70:
        ripeness = "ripe"
    else:
        ripeness = "overripe"

    return {
        "mean_hsv": [float(x) for x in mean_hsv],
        "ripeness": ripeness
    }
