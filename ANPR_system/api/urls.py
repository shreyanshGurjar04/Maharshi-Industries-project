from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cameras', CameraViewSet, basename='camera')
router.register(r'detections', DetectionViewSet, basename='detection')
router.register(r'blacklist', BlacklistViewSet, basename='blacklist')

urlpatterns = [
    path('', include(router.urls)),
    path('ingest/', IngestionAPIView.as_view(), name='ingestion-api'),
    path('video_feed/', video_feed, name='video-feed'),
    path('video_feed/<int:camera_index>/', video_feed, name='video-feed-index'),
    path('infoEntry/', InfoEntry.as_view(), name='test-infoentry'), 
    path('Detections/', TotalDetections.as_view(), name="total_detections"),
    path('Whitelist/', whitelist.as_view(), name="white_detections"),
    path('Blacklist/', Blacklist.as_view(), name="Black_detections"),
    path("clear-detections/", clear_detections, name="clear_detections"),
    path("Report-pdf/", ExportDetectionsPDF.as_view(), name="PDF"),
    path("Report-csv/", ExportDetectionsCSV.as_view(), name="CSV"),
    path("search-detections/", SearchDetections.as_view(), name="search-detections"),


]
