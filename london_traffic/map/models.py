from django.db import models
from django.db.models.deletion import CASCADE

class JamCam(models.Model):
    name = models.CharField(max_length=300, unique=True)
    lat = models.FloatField()
    lon = models.FloatField()


class Capture(models.Model):
    jam_cam = models.ForeignKey(JamCam, on_delete=CASCADE)
    timestamp = models.DateTimeField()
    image_url = models.CharField(max_length=500)
    video_url = models.CharField(max_length=500)
    vehicle_count = models.IntegerField()

    car_count = models.IntegerField()
    motorcycle_count = models.IntegerField()
    bus_count = models.IntegerField()
    truck_count = models.IntegerField()

    class Meta:
        unique_together = ('jam_cam', 'timestamp')
