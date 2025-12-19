import cv2
import json
import time
from pathlib import Path
from src.pipeline import BananaInspectionPipeline

CAPTURE_INTERVAL = 15
COUNTDOWN_SECONDS = 3

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pipeline = BananaInspectionPipeline()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Camera not accessible")

print("Press 'q' to quit")

last_capture_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    time_to_next = CAPTURE_INTERVAL - (now - last_capture_time)
    display = frame.copy()

    if 0 < time_to_next <= COUNTDOWN_SECONDS:
        cv2.putText(
            display,
            f"CAPTURING IN {int(time_to_next) + 1}",
            (50, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 255),
            4
        )

    if time_to_next <= 0:
        results = pipeline.process_frame(frame)
        ts = int(time.time())

        out_file = OUTPUT_DIR / f"banana_sample_{ts}.json"

        payload = {
            "timestamp": ts,
            "detections": results,
            "status": "OK" if results else "NO_VALID_DETECTION"
        }

        with open(out_file, "w") as f:
            json.dump(payload, f, indent=2)

        cv2.imwrite(str(OUTPUT_DIR / f"banana_sample_{ts}.jpg"), frame)

        print(f"[SAVE] Wrote {out_file.name}")
        print(f"[SAVE] Wrote banana_sample_{ts}.jpg")

        last_capture_time = now

    cv2.imshow("Banana Inspection", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
