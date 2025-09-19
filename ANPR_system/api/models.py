from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=100)
    streaming = models.TextField()
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
class Detection(models.Model):
    no_plate = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE,blank=True,null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    video_path = models.CharField(max_length=255,blank=True, null=True)
    blacklist = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.no_plate} -{self.timestamp}"
    
class BlackList(models.Model):
    no_plate = models.CharField(max_length=20, unique=True)
    reason = models.TextField(blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)