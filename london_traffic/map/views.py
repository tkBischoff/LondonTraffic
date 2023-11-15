from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db import connection

import numpy as np
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

def get_quadrants(n):
    """
    Returns a dict with the columns:
        min_lat, max_lat, min_lon, max_lon
    for every quadrant. The london map is 
    divided into <n> rows and <n> columns
    """
    min_lat = 51.3168
    max_lat = 51.6800
    min_lon = -0.49325
    max_lon = 0.23162

    lat_steps = np.linspace(min_lat, max_lat, n+1)
    lon_steps = np.linspace(min_lon, max_lon, n+1)

    quadrants = []

    for i in range(n):
        for j in range(n):
            quadrants.append(
                (
                    lat_steps[i],
                    lat_steps[i+1],
                    lon_steps[j],
                    lon_steps[j+1]
                )
            )

    return quadrants

def in_quadrant(lat, lon, min_lat, max_lat, min_lon, max_lon):
    """
    Returns True if (lat, lon) are in the defined quadrant, else False
    """
    if (lat >= min_lat) and (lat < max_lat) and (lon >= min_lon) and (lon < max_lon):
        return True
    else:
        return False

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
    quadrant_traffic = {}
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
    quadrants = get_quadrants(40)

    for _, row in df.iterrows():
        #traffic_list.append([row['LAT'], row['LON'], row['vehicle_count']])
        jam_cams.append([row['LAT'], row['LON'], row['video_url']])

        for quadrant in quadrants:
            if in_quadrant(row['LAT'], row['LON'], quadrant[0], quadrant[1], quadrant[2], quadrant[3]):
                if quadrant in quadrant_traffic.keys():
                    quadrant_traffic[quadrant].append(row['vehicle_count'])
                else:
                    quadrant_traffic[quadrant] = [row['vehicle_count']]

    for quadrant, traffic_counts in quadrant_traffic.items():
        center_lat = (quadrant[0] +  quadrant[1])/2
        center_lon = (quadrant[2] + quadrant[3])/2
        count_mean = sum(traffic_counts)/len(traffic_counts)

        traffic_list.append([center_lat, center_lon, count_mean])

    return JsonResponse({'traffic_list': traffic_list, 'jam_cams': jam_cams})

