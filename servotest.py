#! /usr/bin/env python3
import RPi.GPIO as GPIO
import time
import asyncio

#pin for servo signal
SIGNAL = 23

#uses broadcom pin names and disables warnings
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#sets the servo signal pin as an output
GPIO.setup(SIGNAL, GPIO.OUT)

servo = GPIO.PWM(SIGNAL, 50)
servo.start(0)

async def turn_servo():
    print("Waiting for 2 seconds")
    await asyncio.sleep(2)

    duty = 2

    while duty <= 12:
        servo.ChangeDutyCycle(duty)
        await asyncio.sleep(1)
        servo.ChangeDutyCycle(0)
        await asyncio.sleep(1)
        duty += 1

    print("Turning back to 90 degrees for 2 seconds")
    servo.ChangeDutyCycle(7)
    await asyncio.sleep(2)

    print("Turning back to 0 degrees")
    servo.ChangeDutyCycle(2)
    await asyncio.sleep(0.5)
    servo.ChangeDutyCycle(0)

    servo.stop()