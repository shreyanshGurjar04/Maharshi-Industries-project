import cv2
import time
import requests
import easyocr
from ultralytics import YOLO
import os
import threading

model = YOLO("license_plate_detector.pt")  
reader = easyocr.Reader(['en'])

os.makedirs("captures/images", exist_ok=True)
os.makedirs("captures/videos", exist_ok=True)

api_url = "http://127.0.0.1:8000/api/infoEntry/"

cap = cv2.VideoCapture(0)
fps = 30
record_seconds = 10

def save_video(frames, video_path, fps=30):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    for f in frames:
        out.write(f)
    out.release()

while True:
    start_loop = time.time()
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO detection
    results = model.predict(frame)

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)

            # Draw bbox in real time
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            plate_img = frame[y1:y2, x1:x2]

            # Save image
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_path = f"captures/images/plate_{timestamp}.jpg"
            cv2.imwrite(image_path, plate_img)

            # Collect frames for 10 seconds
            frames_buffer = []
            end_time = time.time() + record_seconds
            while time.time() < end_time:
                ret_f, f = cap.read()
                if not ret_f:
                    break
                cv2.rectangle(f, (x1, y1), (x2, y2), (0, 255, 0), 2)
                frames_buffer.append(f)
                time.sleep(1/fps)

            # Save video
            video_path = f"captures/videos/plate_{timestamp}.mp4"
            save_video(frames_buffer, video_path, fps)

            # OCR
            ocr_result = reader.readtext(plate_img)
            number_plate = ocr_result[0][1] if ocr_result else "Unknown"

            payload = {
                "no_plate": number_plate,
                "timestamp": timestamp,
                "image_path": image_path,
                "video_path": video_path,
                "Blacklist": False
            }

            try:
                response = requests.post(api_url, json=payload)
                print("API response:", response.status_code, response.text)
            except Exception as e:
                print("Error sending data:", e)

    cv2.imshow("Number Plate Detection", frame)

    # Maintain approx FPS for live feed
    elapsed = time.time() - start_loop
    if elapsed < 1/fps:
        time.sleep(1/fps - elapsed)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
