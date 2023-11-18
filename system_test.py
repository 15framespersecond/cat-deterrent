# Servo Testing - By: fifteenframespersecond - Tue Nov 14 2023

import time
from pyb import Servo
import pyb
import utime
import sensor


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # Turn off auto gain control
sensor.set_auto_whitebal(False)  # Turn off white balance control

s1 = Servo(2) # P8 pan

s2 = Servo(1) # P7 tilt
p = pyb.Pin("P0", pyb.Pin.OUT_PP)
blue_led = pyb.LED(3)

def blink_led():
    for i in range(5):
        blue_led.on()
        utime.sleep_ms(200)
        blue_led.off()
        utime.sleep_ms(200)
    return



while(True):
    img = sensor.snapshot()
    # trigger test
    p.high() # or p.value(1) to make the pin high (3.3V)
    utime.sleep_ms(300)
    p.low()
    blink_led()
    # tilt test
    s2.angle(0) #tilt to 0
    utime.sleep_ms(500)
    s2.angle(45) #tilt to 45
    utime.sleep_ms(500)
    s2.angle(0) # reset to 0

    blink_led()
    # pan test
    s1.angle(0) # pan to 45
    utime.sleep_ms(300)
    s1.angle(45)
    utime.sleep_ms(300)
    s1.angle(0)
    utime.sleep_ms(300)
    s1.angle(-45)
    utime.sleep_ms(300)
    s1.angle(0)
    blink_led()
    blink_led()

