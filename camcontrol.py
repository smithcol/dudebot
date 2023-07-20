#! /usr/bin/env python3
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.vflip = True

def get_image():
    im_path = '/home/pi/dudebot/media/image.jpg'
    camera.capture(im_path)
    return im_path