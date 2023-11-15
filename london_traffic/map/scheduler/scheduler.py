from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

import cv2
import numpy as np
import imutils
import requests
import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from ultralytics import YOLO
from map.models import JamCam, Capture

logger = logging.getLogger(__name__)

model = YOLO('yolov8n.pt')

def count_vehicles_v8(img_url):
    result = model.predict(img_url, save=False)[0]
    res = {'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0}

    for box in result.boxes:
        pred = result.names[box.cls.numpy()[0]]

        if pred in res.keys():
            res[pred] += 1
    return res

def all_jam_cams_v8():
    r = requests.get("https://api.tfl.gov.uk/Place/Type/JamCam/?app_key=7c641a1b1f6e4b04b6fd74edd97e1315")

    for cam in r.json():
        name = cam['commonName']
        lat = cam['lat']
        lon = cam['lon']
        image_url = None
        video_url = None
        ts = None

        properties = cam['additionalProperties']
        for prop in properties:
            if prop['key'] == 'imageUrl':
                image_url = prop['value']
                ts = prop['modified']
            elif prop['key'] == 'videoUrl':
                video_url = prop['value']

        vehicle_counts = count_vehicles_v8(image_url)
        num_vehicles = sum(vehicle_counts.values())

        try:
            cam = JamCam.objects.get(name=name)
        except ObjectDoesNotExist:
            cam = JamCam(name=name, lat=lat, lon=lon)
            cam.save()

        try:
            capture = Capture(
                    jam_cam = cam,
                    timestamp = ts, 
                    image_url = image_url,
                    video_url = video_url, 
                    vehicle_count = num_vehicles,
                    car_count = vehicle_counts['car'],
                    motorcycle_count = vehicle_counts['motorcycle'],
                    bus_count = vehicle_counts['bus'],
                    truck_count = vehicle_counts['truck']
                )
            capture.save()
            logger.warning(f"New capture for {name} at {ts}")
        except IntegrityError:
            logger.warning(f"Capture for {name} at {ts} already exists")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(all_jam_cams_v8, 'interval', minutes=5,
                      name='update_jam_cams', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    logger.warning("startet scheduler")
