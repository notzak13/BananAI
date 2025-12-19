from ultralytics import YOLO

BANANA_CLASS_ID = 46  # COCO banana


class BananaDetector:
    def __init__(self):
        self.model = YOLO("yolov8s-seg.pt")

    def detect_frame(self, frame):
        result = self.model(frame, verbose=False)[0]
        bananas = []

        if result.boxes is None or result.masks is None:
            return bananas

        for i, cls in enumerate(result.boxes.cls):
            if int(cls) != BANANA_CLASS_ID:
                continue

            bananas.append({
                "bbox": result.boxes.xyxy[i].tolist(),
                "confidence": float(result.boxes.conf[i]),
                "mask": result.masks.data[i].cpu().numpy().astype(bool)
            })

        return bananas
