#! /usr/bin/env python3
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.vflip = True

def get_image():
    camera.capture('/home/pi/dudebot/media/image.jpg')