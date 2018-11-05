#!/usr/bin/env python
from datetime import datetime
import datetime
from time import sleep
import time
import picamera
import os
import tinys3
import yaml

# testing
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# photo props
image_width = cfg['image_settings']['horizontal_res']
image_height = cfg['image_settings']['vertical_res']
file_extension = cfg['image_settings']['file_extension']
# file_name = cfg['image_settings']['file_name']
photo_interval = cfg['image_settings']['photo_interval'] # Interval between photo (in seconds)
image_folder = cfg['image_settings']['folder_name']

# camera setup
camera = picamera.PiCamera()
camera.resolution = (image_width, image_height)
camera.awb_mode = cfg['image_settings']['awb_mode']

# Testing Cristian
# camera.iso = 800
#camera.shutter_speed = 20000000
camera.rotation =  270
camera.exposure_mode = 'auto'
# Date timestamp label
camera.annotate_background = picamera.Color('black')
camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#from fractions import Fraction
#camera.framerate = Fraction(1, 6)
#g = camera.awb_gains
#camera.awb_mode = 'auto'
#camera.awb_gains = g

# verify image folder exists and create if it does not
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# camera warm-up time
sleep(2)

# endlessly capture images awwyiss
while True:
    # Build filename string
    filepath = image_folder + '/' + str(int(time.time())) + file_extension
    latest = image_folder + '/' + "latest" + file_extension

    if cfg['debug'] == True:
        print '[debug] Taking photo and saving to path ' + filepath

    # Take Photo
    camera.capture(filepath)
    
    if cfg['debug'] == True:
        print '[debug] Uploading ' + filepath + ' to s3'

    # Upload to S3
    conn = tinys3.Connection(cfg['s3']['access_key_id'], cfg['s3']['secret_access_key'])
    f = open(filepath, 'rb')
    conn.upload(filepath, f, cfg['s3']['bucket_name'])
    conn.upload(latest, f, cfg['s3']['bucket_name'],
               headers={
               'x-amz-meta-cache-control': 'max-age=60'
               })

    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

    # sleep
    sleep(photo_interval)

