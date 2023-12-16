# tennis ball tracker with distance caculater - By: fifteenframespersecond - Wed Nov 8 2023
#
# Prints distance from camera to tennis ball
import sensor
import image
import time
import math
import pyb
import utime
import os
green_led = pyb.LED(2) # select on-board Green LED
green_led.on()
blue_led = pyb.LED(3) #select on-board LED
red_led = pyb.LED(1) # select on-board Red LED

avg_distance_list =[]
avg_distance = []

# Set up the camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # Turn off auto gain control
sensor.set_auto_whitebal(False)  # Turn off white balance control


s2 = pyb.Servo(1)   # create a servo object on position P7
s1 = pyb.Servo(2)   # create a servo object on position P8 PAN
s2.angle(0) #tilt to 0
s1.angle(0)
p = pyb.Pin("P0", pyb.Pin.OUT_PP) # select pin for triggering
p.low()

#take a snapshot of the sill environment
if not "tmp" in os.listdir(): os.mkdir("tmp")
sensor.snapshot().save("tmp/bg.bmp")

# Tennis ball color range (adjust these values for your specific environment)
#threshold = (60, 110, -30, -10, -7, 40)
#threshold = (60, 110, -40, 15, 0, 50)
#threshold = (30, 60, 25, 65, 10, 70) # threshold for red

threshold_rgb = (50, 100, 75, 150, 75, 255)  # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
threshold_lab = (30, 110, -60, 50, -60, 50)  # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
# Variables for tracking
threshold_rgb = (50, 90, 80, 150, 75, 200)  # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
threshold_lab = (30, 40, -40, 40, -50, 0)

threshold_rgb = (50, 100, 80, 140, 75, 255)  # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
threshold_lab = (45, 60, 0, 25, -50, 0)

threshold_rgb = (50, 110, 80, 225, 100, 255)  # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
threshold_lab = (40, 50, -40, 25, -50, 5)

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

###threshold_lab = (58, 100, 15, 127, 28, 74) # threshold for red!!!!!!
###threshold_lab = (51, 100, 15, 127, 23, 75) # threshold for red DEC 7 3:28pm
#threshold_lab = (59, 92, -16, -37, 23, 54)#fatherst distance
## above is tennis ball, below is cottonball

#threshold_lab = (10, 55, 15, 40, -75, -50)
prev_center = (0, 0)
prev_time = 0

# Values to calculate distance
lens_mm = 2.8 # Standard Lens.
average_object_height_mm = 64.9 # tennis ball measured in
#average_object_height_mm = 80.0 # red object
image_height_pixels = 240.0 # QVGA
image_width_pixels = 320.0
sensor_h_mm = 2.952 # For OV7725 sensor - see datasheet.
offest_mm = -100.0 # Offset fix.

# Function to calculate distance from camera to object
def rect_size_to_distance(r): # r == (x, y, w, h) -> r[3] == h
    return ((lens_mm * average_object_height_mm * image_height_pixels) / (r[3] * sensor_h_mm)) - offest_mm

# Camera field of view (in degrees)
horizontal_fov = 70.8  # QVGA
vertical_fov = 55.6  # QVGA

def calculate_pan_angle(ball_x, image_width, distance_mm):
    # Calculate the horizontal angle to the object (in degrees)
    relative_x = (ball_x - (image_width / 2))  # Calculate the position relative to the image center
    horizontal_angle = (relative_x / image_width) * horizontal_fov

    # Calculate the horizontal distance to the ball (in mm) using trigonometry
    horizontal_distance = distance_mm * math.tan(math.radians(horizontal_angle))

    # Now, you can use trigonometry to calculate the pan angle based on the horizontal distance
    # and the distance to the ball (Pythagoras' theorem)
    pan_angle = math.degrees(math.atan2(horizontal_distance, distance_mm))

    return pan_angle

def calculate_tilt_angle(ball_y, image_height, distance_mm):
    # Calculate the vertical angle to the ball (in degrees)
    relative_y = (ball_y - (image_height / 2))  # Calculate the position relative to the image center
    vertical_angle = (relative_y / image_height) * vertical_fov

    # Calculate the vertical distance to the ball (in mm) using trigonometry
    vertical_distance = distance_mm * math.tan(math.radians(vertical_angle))

    # Now, you can use trigonometry to calculate the tilt angle based on the vertical distance
    # and the distance to the ball (Pythagoras' theorem)
    tilt_angle = math.degrees(math.atan2(vertical_distance, distance_mm))

    return tilt_angle

turret_height = 96.0 # in mm
turret_height = 33.0 # in mm
water_velocity = 11073.0 # in mm/s
water_velocity = 14174.0
g = 9810.0
def calculate_tilt_angle2(distance_mm):
    # Calculate the tilt angle accounting for gravitational drop-off
    tilt_angle = math.degrees(math.asin((g * distance_mm) / (water_velocity**2)))

    # Adjust the tilt angle based on the height of the turret
    turret_drop = turret_height * math.tan(math.radians(tilt_angle))
    corrected_tilt_angle = math.degrees(math.atan2(turret_drop, distance_mm))

    return corrected_tilt_angle


def calculate_tilt_angle3(distance_mm):
    tilt_angle = math.degrees((distance_mm * g) / (2 * water_velocity**2) - (2* turret_height / distance_mm))
    return tilt_angle

def blink_led():
    for i in range(5):
        blue_led.on()
        utime.sleep_ms(200)
        blue_led.off()
        utime.sleep_ms(200)
    return

def roundness_check(blobs):
    round_list = []
    for i in range(len(blobs)):
        round_list.append(blobs[i].roundness())
    roundness_max = max(round_list)
    roundest_blob_index = round_list.index(roundness_max)
    if roundness_max > .2:
        check = 1
    else:
        check = 0
    return check, roundest_blob_index
    blink_led()


def avg(list_arr):
    total = 0
    for i in range(len(list_arr)):
        total = total + list_arr[i]
    return total/len(list_arr)



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


    img = sensor.snapshot()

    #hist = get_histogram(1).b_value

    # Motion detection
    #img.difference("tmp/bg.bmp")
    hist = img.get_histogram()
    #hist_intial = img.get_histogram()
    diff_t = hist.get_percentile(0.99).l_value() - hist.get_percentile(0.90).l_value()
    #print(diff_t)
    if diff_t < 28:

        blobs = img.find_blobs([threshold_lab], pixels_threshold=35, area_threshold=35)
        if blobs:
            round_bool, roundest_blob_index = roundness_check(blobs)
            if round_bool == 1:
                # Find the largest detected blob (the tennis ball)
                max_blob = max(blobs, key=lambda b: b.pixels()) # maybe can get ride of?
                img.draw_rectangle(blobs[roundest_blob_index].rect(), color=(0, 255, 0))  # Draw a green rectangle around the ball
                img.draw_cross(blobs[roundest_blob_index].cx(), blobs[roundest_blob_index].cy(), color=(0, 255, 0))  # Draw a green cross at the ball's center
                # Draw cross in center of screen
                img.draw_cross(img.width()//2, img.height()//2, size = min(img.width()//5, img.height()//5))
                # Draw distance
                img.draw_string(blobs[roundest_blob_index][0] - 16, blobs[roundest_blob_index][1] - 16, "Distance %d mm" % rect_size_to_distance(blobs[roundest_blob_index]))
                #print( "Distance %d mm" % rect_size_to_distance(blobs[roundest_blob_index]))
                # build average distance over 10 frames, once built aim and trigger water gun
                if 5 <= len(avg_distance_list):
                    avg_distance = avg(avg_distance_list)
                    print("distance", avg_distance)
                    s1.angle(-calculate_pan_angle(blobs[roundest_blob_index].cx(), image_width_pixels, avg_distance))
                    #s2.angle(-calculate_pan_angle(blobs[roundest_blob_index].cy(), image_width_pixels, avg_distance))
                    #print("tilt angle: ", -calculate_tilt_angle(blobs[roundest_blob_index].cy(), image_width_pixels, avg_distance))
                    s2.angle(-calculate_tilt_angle2(avg_distance))
                    print("tilt angle:",-calculate_tilt_angle2(avg_distance))
                    #s2.angle(-calculate_tilt_angle2(blobs[roundest_blob_index].cy(), image_height_pixels, avg_distance))
                    red_led.on()
                    p.high() # or p.value(1) to make the pin high (3.3V)
                    utime.sleep_ms(300)
                    p.low()
                    red_led.off()
                    avg_distance_list = []
                else:
                    avg_distance_list.append(rect_size_to_distance(blobs[roundest_blob_index]))

                #utime.sleep_ms(200)
                #blink_led()
                #print(rect_size_to_distance(blobs[i])) #debug
 #magic numbers to calibrate tilt angle
                #p.high() # or p.value(1) to make the pin high (3.3V)
                #utime.sleep_ms(100)

                #print(-2*calculate_tilt_angle(max_blob.cy(), image_height_pixels, rect_size_to_distance(blobs[i]))) #debug
            # Calculate motion tracking(not used yet but should predict speed of object moving)
            current_time = time.ticks_ms()
            if prev_center != (0, 0):
                delta_time = time.ticks_diff(current_time, prev_time)
                delta_x = max_blob.cx() - prev_center[0]
                delta_y = max_blob.cy() - prev_center[1]
                speed = math.sqrt(delta_x ** 2 + delta_y ** 2) / delta_time
                #print("Speed:", speed, "pixels/ms")

                prev_center = (max_blob.cx(), max_blob.cy())
                prev_time = current_time










