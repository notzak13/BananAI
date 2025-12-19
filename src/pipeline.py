from src.detect import BananaDetector
from src.geometry import estimate_length
from src.color import analyze_color
from src.quality import estimate_shelf_life, quality_score


class BananaInspectionPipeline:
    def __init__(self):
        self.detector = BananaDetector()

    def process_frame(self, frame):
        bananas = self.detector.detect_frame(frame)
        print(f"[PIPELINE] Detected {len(bananas)} bananas")

        results = []

        for b in bananas:
            length = estimate_length(b["mask"])
            print(f"[PIPELINE] Estimated length: {length}")

            if length is None:
                print("[PIPELINE] ❌ Length invalid")
                continue

            color = analyze_color(frame, b["mask"])
            shelf = estimate_shelf_life(color["ripeness"])
            quality = quality_score(length, b["confidence"], color["ripeness"])

            results.append({
                "confidence": round(b["confidence"], 3),
                "length_cm": length,
                "ripeness": color["ripeness"],
                "mean_hsv": color["mean_hsv"],
                "shelf_life_days": shelf,
                "quality_score": round(quality, 2),
            })

        print(f"[PIPELINE] Final results count: {len(results)}")
        return results
