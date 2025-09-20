from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import *
from .serializers import *
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import StreamingHttpResponse
import cv2
from ultralytics import YOLO
import easyocr
import numpy as np
import requests
from datetime import datetime
import os
import threading
import time
import torch
from rest_framework.decorators import api_view
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import csv
from datetime import datetime

# ==================== ViewSets ====================

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.all().order_by("-timestamp")
    serializer_class = DetectionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
@api_view(['DELETE'])
def clear_detections(request):
    Detection.objects.all().delete()
    return Response({"message": "All detections deleted successfully"})

class BlacklistViewSet(viewsets.ModelViewSet):
    queryset = BlackList.objects.all()
    serializer_class = BlacklistSerializer

# ==================== Detection Page ====================

class TotalDetections(APIView):
    def get(self, request):
        try:
            count = Detection.objects.count()
            return Response({"Total Detection": count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ==================== WhiteList Page ====================

class whitelist(APIView):
    def get(self, request):
        try:
            detections = Detection.objects.filter(blacklist=False)
            serializer = DetectionSerializer(detections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Use 500 for server errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== BlackList Page ====================

class Blacklist(APIView):
    def get(self, request):
        try:
            detections = Detection.objects.filter(blacklist=True)
            serializer = DetectionSerializer(detections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== InfoEntry API ====================

class InfoEntry(APIView):
    def post(self, request):
        try:
            no_plate = request.data.get('no_plate')
            timestamp = request.data.get('timestamp', timezone.now())
            image_path = request.data.get('image_path', '')
            video_path = request.data.get('video_path', '')
            blacklist_flag = request.data.get('blacklist', False)

            is_blacklisted = BlackList.objects.filter(no_plate=no_plate).exists()
            if is_blacklisted:
                blacklist_flag = True
                subject = f"Blacklist Alert: {no_plate}"
                message = f"Alert! Blacklisted vehicle detected: {no_plate}"
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                          settings.ALERT_EMAIL_RECIPIENTS, fail_silently=False)

            detection = Detection.objects.create(
                no_plate=no_plate,
                timestamp=timestamp,
                image_path=image_path,
                video_path=video_path,
                blacklist=blacklist_flag
            )
            serializer = DetectionSerializer(detection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            detection = Detection.objects.all()
            serializer = DetectionSerializer(detection, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== Ingestion API ====================

class IngestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        required_fields = ["camera_id", "license_plate", "confidence", "timestamp"]
        for field in required_fields:
            if field not in data:
                return Response({"error": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            camera = Camera.objects.get(id=data["camera_id"])
        except Camera.DoesNotExist:
            return Response({"error": "Camera not found"}, status=status.HTTP_404_NOT_FOUND)

        detection = Detection.objects.create(
            camera=camera,
            license_plate=data["license_plate"],
            confidence=data["confidence"],
            timestamp=data["timestamp"]
        )
        serializer = DetectionSerializer(detection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ==================== Real-time Video Feed ====================

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using GPU")
else:
    device = torch.device("cpu")
    print("Using CPU")

model = YOLO("best2.pt").to(device) #latest model best2.pt

reader = easyocr.Reader(['en'], gpu=torch.backends.mps.is_available())
 
API_URL = "http://127.0.0.1:8000/api/infoEntry/"

os.makedirs("detected_plates", exist_ok=True)
os.makedirs("detected_videos", exist_ok=True)

VIDEO_FPS = 10 
MAX_RECORD_SECONDS = 45
PLATE_MISSING_FRAMES = 1

# ==================== Helper Functions ====================

def preprocess_plate(plate_img):
    if plate_img is None or plate_img.size == 0:
        return plate_img
    try:
        if len(plate_img.shape) == 3 and plate_img.shape[2] == 3:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_img
        gray = cv2.equalizeHist(gray)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        h, w = thresh.shape
        resized = cv2.resize(thresh, (w * 2, h * 2), interpolation=cv2.INTER_LINEAR)
        return resized
    except Exception as e:
        print(f"[PREPROCESS ERROR] {e}")
        return plate_img


def save_plate(no_plate, timestamp, plate_img, video_frames):
    try:
        if not no_plate:
            no_plate = "unknown"
        if plate_img is None or (hasattr(plate_img, 'size') and plate_img.size == 0):
            return
        # sanitize filename
        safe_plate = ''.join(c for c in no_plate if c.isalnum() or c in ('_', '-'))
        image_path = f"detected_plates/{safe_plate}_{timestamp}.jpg"
        video_path = f"detected_videos/{safe_plate}_{timestamp}.mp4"
        cv2.imwrite(image_path, plate_img)
        if video_frames:
            h, w, _ = video_frames[0].shape
            out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), VIDEO_FPS, (w, h))
            for f in video_frames:
                out.write(f)
            out.release()
        payload = {
            "no_plate": no_plate,
            "timestamp": timestamp,
            "image_path": image_path,
            "video_path": video_path,
            "blacklist": False
        }
        try:
            requests.post(API_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"[API ERROR] {e}")
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

# ==================== Frame Generator ====================

def generate_frames(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[CAM ERROR] Cannot open camera")
        return

    last_plate = ""
    video_buffer = []
    missing_plate_counter = 0
    best_plate_frame = None
    best_plate_bbox = None
    PLATE_LOST_THRESHOLD = 30
    TARGET_FPS = VIDEO_FPS
    FRAME_INTERVAL = 1.0 / TARGET_FPS
    CONF_THRESHOLD = 0.35

    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success or frame is None:
            time.sleep(0.01)
            continue

        plate_detected_this_frame = False

        try:
            results = model.predict(frame, imgsz=640, conf=CONF_THRESHOLD, verbose=False)
            detected_plate_in_frame = None
            detected_bbox = None
            detected_conf = 0.0

            for result in results:
                for box in result.boxes:
                    try:
                        xyxy = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1, x2, y2 = xyxy.tolist()
                        conf = float(box.conf[0]) if hasattr(box, 'conf') else float(box.conf)
                        if conf < CONF_THRESHOLD:
                            continue
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1]-1, x2), min(frame.shape[0]-1, y2)
                        if x2 <= x1 or y2 <= y1:
                            continue

                        plate_img = frame[y1:y2, x1:x2].copy()
                        plate_proc = preprocess_plate(plate_img)
                        if plate_proc is None or (hasattr(plate_proc, 'size') and plate_proc.size == 0):
                            continue

                        # OCR
                        try:
                            ocr_result = reader.readtext(plate_proc)
                            tokens = [t for t in ocr_result if len(t) >= 3 and t[2] > 0.4]
                            detected_plate = ''.join([t[1] for t in tokens]) if tokens else ''
                        except Exception as e:
                            print(f"[OCR ERROR] {e}")
                            detected_plate = ''

                        if detected_plate:
                            plate_detected_this_frame = True
                            area = (x2-x1)*(y2-y1)
                            score = area * conf
                            if score > detected_conf:
                                detected_conf = score
                                detected_plate_in_frame = detected_plate
                                detected_bbox = (x1, y1, x2, y2)

                    except Exception as e:
                        print(f"[BOX ERROR] {e}")
                        continue
            if plate_detected_this_frame and detected_plate_in_frame:
                if detected_plate_in_frame != last_plate:
                    last_plate = detected_plate_in_frame
                    missing_plate_counter = 0
                if best_plate_frame is None or (detected_bbox and (detected_bbox[2]-detected_bbox[0])*(detected_bbox[3]-detected_bbox[1]) > ((best_plate_bbox[2]-best_plate_bbox[0])*(best_plate_bbox[3]-best_plate_bbox[1]) if best_plate_bbox else 0)):
                    best_plate_frame = frame.copy()
                    best_plate_bbox = detected_bbox

        except Exception as e:
            print(f"[PREDICT ERROR] {e}")

        if last_plate:
            try:
                # Check blacklist status
                is_blacklisted = BlackList.objects.filter(no_plate=last_plate).exists()
                color = (0, 0, 255) if is_blacklisted else (0, 255, 0)  # Red if blacklist else Green

                overlay = frame.copy()
                cv2.rectangle(overlay, (40, 10), (400, 80), (0, 0, 0), -1)  
                frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)  

                cv2.putText(frame, f"Plate: {last_plate}",
                            (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, color, 2, cv2.LINE_AA)

                text_size = cv2.getTextSize(f"Plate: {last_plate}",
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                text_x, text_y = 50, 50
                cv2.line(frame, (text_x, text_y + 5),
                         (text_x + text_size[0], text_y + 5), color, 3)

            except Exception as e:
                print(f"[DRAW ERROR] {e}")


        if plate_detected_this_frame or missing_plate_counter < PLATE_LOST_THRESHOLD:
            video_buffer.append(frame.copy())

            max_buffer = int(MAX_RECORD_SECONDS * VIDEO_FPS)
            if len(video_buffer) > max_buffer:
                video_buffer.pop(0)

        if not plate_detected_this_frame:
            missing_plate_counter += 1


        if missing_plate_counter >= PLATE_LOST_THRESHOLD and video_buffer:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            if best_plate_frame is not None and best_plate_bbox is not None:
                x1, y1, x2, y2 = best_plate_bbox
                clear_img = best_plate_frame[y1:y2, x1:x2].copy()

                threading.Thread(target=save_plate, args=(last_plate, ts, clear_img, video_buffer.copy()), daemon=True).start()
            video_buffer.clear()
            best_plate_frame = None
            best_plate_bbox = None
            last_plate = ""
            missing_plate_counter = 0

        try:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"[ENCODE ERROR] {e}")

        elapsed = time.time() - start_time
        sleep_time = max(0, FRAME_INTERVAL - elapsed)
        time.sleep(sleep_time)

# ==================== Video Feed API ====================

def video_feed(request, camera_index=0):
    return StreamingHttpResponse(generate_frames(camera_index), content_type='multipart/x-mixed-replace; boundary=frame')

# ==================== PDF API ====================

class ExportDetectionsPDF(APIView):

    def get(self, request, format=None):
        try:
            queryset = Detection.objects.all()

            # Apply filters
            plate = request.query_params.get("plate")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            blacklist = request.query_params.get("blacklist")
            export_format = request.query_params.get("format", "pdf")  # default PDF

            if plate:
                queryset = queryset.filter(no_plate__icontains=plate)
            if start_date and end_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])
            if blacklist is not None:
                queryset = queryset.filter(blacklist=(blacklist.lower() == "true"))

            # --- CSV Export ---
            if export_format == "csv":
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = 'attachment; filename="detections.csv"'

                writer = csv.writer(response)
                writer.writerow(["Plate", "Timestamp", "Camera", "Blacklist", "Image Path", "Video Path"])
                for det in queryset:
                    writer.writerow([
                        det.no_plate,
                        det.timestamp,
                        det.camera.name if det.camera else "N/A",
                        det.blacklist,
                        det.image_path,
                        det.video_path
                    ])
                return response

            elif export_format == "pdf":
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []

                data = [["Plate", "Timestamp", "Camera", "Blacklist", "Image Path", "Video Path"]]
                for det in queryset:
                    data.append([
                        det.no_plate,
                        det.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        det.camera.name if det.camera else "N/A",
                        "Yes" if det.blacklist else "No",
                        det.image_path,
                        det.video_path
                    ])

                table = Table(data, repeatRows=1)
                style = TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.grey),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                    ("ALIGN", (0,0), (-1,-1), "CENTER"),
                    ("GRID", (0,0), (-1,-1), 0.5, colors.black),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,-1), 10),
                ])
                table.setStyle(style)
                elements.append(table)

                doc.build(elements)
                buffer.seek(0)

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                filename = f"detections_{timestamp}.pdf"

                response = HttpResponse(buffer, content_type="application/pdf")
                response['Content-Disposition'] = f'attachment; filename="{filename}"'  # force download
                return response

            else:
                return Response({"error": "Unsupported format"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== CSV API ====================

class ExportDetectionsCSV(APIView):
    def get(self, request, format=None):
        try:
            queryset = Detection.objects.all()

            plate = request.query_params.get("plate")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            blacklist = request.query_params.get("blacklist")
            export_format = request.query_params.get("format", "csv") 

            if plate:
                queryset = queryset.filter(no_plate__icontains=plate)
            if start_date and end_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])
            if blacklist is not None:
                queryset = queryset.filter(blacklist=(blacklist.lower() == "true"))

            if export_format == "csv":
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = 'attachment; filename="detections.csv"'

                writer = csv.writer(response)
                writer.writerow(["Plate", "Timestamp", "Camera", "Blacklist", "Image Path", "Video Path"])
                for det in queryset:
                    writer.writerow([
                        det.no_plate,
                        det.timestamp,
                        det.camera.name if det.camera else "N/A",
                        det.blacklist,
                        det.image_path,
                        det.video_path
                    ])
                return response

            elif export_format == "pdf":
                buffer = BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                p.setFont("Helvetica", 12)

                y = 750
                p.drawString(30, y, "License Plate Detection Report")
                y -= 30

                for det in queryset:
                    text = f"{det.no_plate} | {det.timestamp} | {det.camera.name if det.camera else 'N/A'} | Blacklist: {det.blacklist}"
                    p.drawString(30, y, text)
                    y -= 20
                    if y < 50:
                        p.showPage()
                        y = 750

                p.save()
                buffer.seek(0)
                return HttpResponse(buffer, content_type="application/pdf")

            else:
                return Response({"error": "Unsupported format"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Search API ====================

from django.db.models import Q

class SearchDetections(APIView):
    def get(self, request):
        try:
            queryset = Detection.objects.all()

            plate = request.query_params.get("plate")
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            blacklist = request.query_params.get("blacklist")

            if plate:
                q = Q()
                for char in plate:
                    q |= Q(no_plate__icontains=char)
                queryset = queryset.filter(q)

            if start_date and end_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])
            if blacklist is not None and blacklist != "":
                queryset = queryset.filter(blacklist=(blacklist.lower() == "true"))

            serializer = DetectionSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
