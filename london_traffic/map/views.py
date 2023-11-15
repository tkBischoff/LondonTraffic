from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db import connection
import logging
import requests
import pandas as pd

logger = logging.getLogger(__name__)

def my_view(request):
    logging.warning("Loading map view")
    maps_api_key = None
    context = {
        #'maps_api_key': MAPS_API_KEY
    }
    return render(request, 'map/index.html', context)


def traffic_video(request):
    lat = None
    lon = None

    if request.method == 'GET':
        lat = request.GET['lat']
        lon = request.GET['lon']

    qry = """
    WITH cte_max_ts AS
        ( SELECT id, MAX(timestamp) AS timestamp FROM map_capture GROUP BY id )
    SELECT 
        capture.video_url AS video_url
    FROM map_capture capture
    INNER JOIN cte_max_ts max_ts 
        ON 
            capture.ID = max_ts.ID 
            AND capture.timestamp = max_ts.timestamp
    INNER JOIN map_jamcam cam
        ON 
            capture.ID = cam.ID;
    WHERE
        cam.lat = {}
        AND cam.lon = {}
    """.format(lat, lon)
    df = pd.read_sql_query(qry, connection)
    video_url = df.loc[0, "video_url"].values[0]
    return JsonResponse({'video_url': video_url})


def traffic(request):
    """
    Return a JSON of the folllowing shape:
    [
        [lat1, lon1, cars1],
        [lat2, lon2, cars2],
        ...
        [latn, lonn, carsn]
    ]
    """
    traffic_list = []
    jam_cams = []
    qry = """
    WITH cte_max_ts AS
        ( SELECT id, MAX(timestamp) AS timestamp FROM map_capture GROUP BY id )
    SELECT 
        cam.id AS ID,
        cam.lat AS LAT,
        cam.lon AS LON,
        capture.vehicle_count AS vehicle_count,
        capture.video_url AS video_url
    FROM map_capture capture
    INNER JOIN cte_max_ts max_ts 
        ON 
            capture.ID = max_ts.ID 
            AND capture.timestamp = max_ts.timestamp
    INNER JOIN map_jamcam cam
        ON 
            capture.ID = cam.ID;
    """

    df = pd.read_sql_query(qry, connection)

    for _, row in df.iterrows():
        traffic_list.append([row['LAT'], row['LON'], row['vehicle_count']])
        jam_cams.append([row['LAT'], row['LON'], row['video_url']])


    return JsonResponse({'traffic_list': traffic_list, 'jam_cams': jam_cams})

