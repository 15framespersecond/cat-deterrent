# object tracker with distance caculater - By: fifteenframespersecond
#
# 
import sensor
import image
import time
import math
import pyb
import utime
import os
### Initialize on-board pins
green_led = pyb.LED(2) # select on-board Green LED
green_led.on() # turn on green LED while intializing
blue_led = pyb.LED(3) #select on-board LED
red_led = pyb.LED(1) # select on-board Red LED
tilt_servo = pyb.Servo(1)   # create a servo object on position P7 TILT
pan_servo = pyb.Servo(2)   # create a servo object on position P8 PAN
tilt_servo.angle(0) # zero out tilt
pan_servo.angle(0) # zero out pan
watergun_trigger = pyb.Pin("P0", pyb.Pin.OUT_PP) # select pin for watergun triggering
watergun_trigger.low() # zero out watergun trigger, sometimes pin is stuck in HIGH state if now specified

### Set up the camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # Turn off auto gain control
sensor.set_auto_whitebal(False)  # Turn off white balance control

# Take a snapshot of the sill environment
if not "tmp" in os.listdir(): os.mkdir("tmp") # create directory to save intial reference image
sensor.snapshot().save("tmp/bg.bmp") # image saved

### Variables Intialization 
# note thresholds are set for specific objects, previous ones used are left in comments in case we want to revert or to see changes in needed thresholds 
#threshold = (60, 110, -30, -10, -7, 40)
#threshold = (60, 110, -40, 15, 0, 50)
#threshold = (30, 60, 25, 65, 10, 70) # threshold for red

#threshold_lab = (80, 100, -60, 0, 0, 55) # this work!
#threshold_lab = (73, 100, -68, -10, 9, 57) # and this maybe? with machine vision tuning
#threshold_lab = (70, 100, -48, 2, 6, 58)
#threshold_lab = (68, 100, -62, 0, 17, 68)
#threshold_lab = (68, 100, -62, 0, 23, 68)

#threshold_lab = (58, 93, -26, -68, 34, 61) # dec1 12:13pm
threshold_lab = (54, 100, -21, -93, 12, 84) #dec1 12:16pm
threshold_lab = (54, 100, -30, -93, 30, 79) # WORKING DEC 1 12:53PM
threshold_lab = (54, 100, -30, -93, 41, 79) # DEC 6 4pm
threshold_lab = (43, 100, -81, -28, 40, 92)# DEC 7 3:38pm tennis ball

#threshold_lab = (41, 100, 6, 32, -83, -32) # DEC 10 11:08AM

###threshold_lab = (58, 100, 15, 127, 28, 74) # threshold for red!!!!!!
###threshold_lab = (51, 100, 15, 127, 23, 75) # threshold for red DEC 7 3:28pm
#threshold_lab = (59, 92, -16, -37, 23, 54)#fatherst distance
## above is tennis ball, below is cottonball
#threshold_lab = (0, 100, 6, 28, -64, -46) # dec 10 cotton 11:42AM

#threshold_lab = (10, 55, 15, 40, -75, -50)
#threshold_lab = (46, 100, 0, 21, -84, -40)
threshold_lab = (36, 100, -2, 44, -72, -41)
#threshold_lab = (0, 100, -128, 127, -7, -10) # cat paper
threshold_lab = (39, 100, -22, 11, -66, -21)
threshold_lab = (42, 100, -16, 16, -60, -44)

# Values to calculate distance
lens_mm = 2.8 # Standard Lens.
average_object_height_mm = 64.9 # tennis ball measured in
#average_object_height_mm = 80.0 # red object
average_object_height_mm = 210.0 # height of large cotton ball
image_height_pixels = 240.0 # QVGA specs
image_width_pixels = 320.0
sensor_h_mm = 2.952 # For OV7725 sensor - see datasheet.
offest_mm = 0.0 # Offset fix if needed
# Create Empty Lists
avg_distance_list =[]
avg_distance = []# Camera field of view (in degrees)
# FOVs used in pan/tilt
horizontal_fov = 70.8  # QVGA camera
vertical_fov = 55.6  # QVGA camera
# Kinematic Values
turret_height = 96.0 # in mm
water_velocity = 11073.0 # in mm/s
g = 9810.0

### Functions
def rect_size_to_distance(r): # r == (x, y, w, h) -> r[3] == h
    return ((lens_mm * average_object_height_mm * image_height_pixels) / (r[3] * sensor_h_mm)) - offest_mm

def calculate_pan_angle(ball_x, image_width, distance_mm):
    # Calculate the horizontal angle to the object (in degrees)
    relative_x = (ball_x - (image_width / 2))  # Calculate the position relative to the image center
    horizontal_angle = (relative_x / image_width) * horizontal_fov
    # Calculate the horizontal distance to the ball (in mm) using trigonometry
    horizontal_distance = distance_mm * math.tan(math.radians(horizontal_angle))
    # Trigonometry to calculate the pan angle based on the horizontal distance
    pan_angle = math.degrees(math.atan2(horizontal_distance, distance_mm))
    return pan_angle

def calculate_tilt_angle(ball_y, image_height, distance_mm): # orginal tilt function assuming laser projectile with no drop off
    # Calculate the vertical angle to the ball (in degrees)
    relative_y = (ball_y - (image_height / 2))  # Calculate the position relative to the image center
    vertical_angle = (relative_y / image_height) * vertical_fov
    # Calculate the vertical distance to the ball (in mm) using trigonometry
    vertical_distance = distance_mm * math.tan(math.radians(vertical_angle))
    # Trigonometry to calculate the tilt angle based on the vertical distance
    tilt_angle = math.degrees(math.atan2(vertical_distance, distance_mm)*1.15)
    return tilt_angle


def calculate_tilt_angle_with_kinematics(distance_mm):
    tilt_angle = math.degrees((distance_mm * g) / (water_velocity**2))
    return tilt_angle

def blink_led(): #debugging function used to slow down opperation and inspect steps
    for i in range(5):
        blue_led.on()
        utime.sleep_ms(200)
        blue_led.off()
        utime.sleep_ms(200)
    return


def avg(list_arr): # take average of list
    total = 0
    for i in range(len(list_arr)):
        total = total + list_arr[i]
    return total/len(list_arr)

# flash green led to indicate end of intialization and beginning of normal operation
green_led.off()
utime.sleep_ms(100)
green_led.on()
utime.sleep_ms(100)
green_led.off()
utime.sleep_ms(100)
green_led.on()
utime.sleep_ms(100)
green_led.off()
while True:

    img = sensor.snapshot() # take current snapshot/image and save as image object in 'img' var

    # Motion detection
    img_ref = img.difference("tmp/bg.bmp") # create image object from the snapshot taken during intialization
    hist_ref = img_ref.get_histogram() # get the normalized histo for the reference image
    hist = img.get_histogram() # get the normalized histo for the current image
    brightness_change = hist_ref.get_percentile(0.99).l_value() - hist.get_percentile(0.90).l_value() # track brightness change, L-value, from reference image and current image
    #print(brightness_change) #debugging
    blue_led.off() # ensure blue LED is off while no object in view
    # Motion Detected
    if brightness_change > 10:
        #print("active") # debugging
        blobs = img.find_blobs([threshold_lab], pixels_threshold=20, area_threshold=20)
        if blobs:
            #print("BLOBS") # debugging
            # Find the largest detected blob
            max_blob = max(blobs, key=lambda b: b.pixels()) # grab the largest blob
            # Draw objects in frame buffer for testing, calibration, and debugging
            img.draw_rectangle(max_blob.rect(), color=(0, 255, 0))  # Draw a green rectangle around the ball
            img.draw_cross(max_blob.cx(), max_blob.cy(), color=(0, 255, 0))  # Draw a green cross at the ball's center
            # Draw cross in center of screen 
            img.draw_cross(img.width()//2, img.height()//2, size = min(img.width()//5, img.height()//5))
            # Draw distance on top of bound object
            img.draw_string(max_blob[0] - 16, max_blob[1] - 16, "Distance %d mm" % rect_size_to_distance(max_blob))
            # Build average distance over 5 frames, once built aim and trigger water gun
            if 5 <= len(avg_distance_list): # activateds once built large enough avg
                avg_distance = avg(avg_distance_list)
                #print("distance: ", avg_distance) # debugging
                pan_servo.angle(-calculate_pan_angle(max_blob.cx(), image_width_pixels, avg_distance)+6)
                tilt_anlge = calculate_tilt_angle_with_kinematics(avg_distance)
                if tilt_angle < 0: # turret cannot aim below 0 degrees
                    blue_led.on() # blue LED flashes on if below threshold and water gun is not triggered
                else:
                    blue_led.off() 
                    tilt_servo.angle(tilt_angle) # tilt to angle to it target
                    red_led.on() 
                    watergun_trigger.high() # can also use watergun_trigger.value(1) to make the pin high (3.3V)
                    utime.sleep_ms(300) # quick spirt of water, is possible to remove delay and average but a lot of water will be continously shot at single target
                    watergun_trigger.low()
                    red_led.off()
                avg_distance_list = [] # reset average list
            else:
                avg_distance_list.append(rect_size_to_distance(max_blob)) # build average


