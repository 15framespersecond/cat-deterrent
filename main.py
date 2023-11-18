# tennis ball tracker with distance caculater - By: fifteenframespersecond - Wed Nov 8 2023
#
# Prints distance from camera to tennis ball
import sensor
import image
import time
import math
import pyb
import utime
# Set up the camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # Turn off auto gain control
sensor.set_auto_whitebal(False)  # Turn off white balance control
s2 = pyb.Servo(1)   # create a servo object on position P7
s1 = pyb.Servo(2)   # create a servo object on position P8 PAN
p = pyb.Pin("P0", pyb.Pin.OUT_PP) # select pin for triggering
blue_led = pyb.LED(3) #select on-board LED

# Tennis ball color range (adjust these values for your specific environment)
threshold = (60, 110, -30, -10, -7, 40) # HUE_MIN, HUE_MAX, SAT_MIN, SAT_MAX, VAL_MIN, VAL_MAX
threshold = (30, 60, 25, 65, 10, 70) # threshold for red
# Variables for tracking
prev_center = (0, 0)
prev_time = 0

# Values to calculate distance
lens_mm = 2.8 # Standard Lens.
average_object_height_mm = 64.9 # tennis ball measured in mm
image_height_pixels = 240.0 # QVGA
image_width_pixels = 320.0
sensor_h_mm = 2.952 # For OV7725 sensor - see datasheet.
offest_mm = 100.0 # Offset fix.

# Function to calculate distance from camera to object
def rect_size_to_distance(r): # r == (x, y, w, h) -> r[3] == h
    return ((lens_mm * average_object_height_mm * image_height_pixels) / (r[3] * sensor_h_mm)) - offest_mm

# Camera field of view (in degrees)
horizontal_fov = 70.8  # QVGA
vertical_fov = 55.6  # QVGA

def calculate_pan_angle(ball_x, image_width, distance_mm):
    # Calculate the horizontal angle to the ball (in degrees)
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

def blink_led(): 
    for i in range(5):
        blue_led.on()
        utime.sleep_ms(200)
        blue_led.off()
        utime.sleep_ms(200)
    return

while True:
    img = sensor.snapshot()

    # Color detection
    blobs = img.find_blobs([threshold], pixels_threshold=200, area_threshold=200)


    if blobs:
        # Find the largest detected blob (the tennis ball)
        max_blob = max(blobs, key=lambda b: b.pixels())
        img.draw_rectangle(max_blob.rect(), color=(0, 255, 0))  # Draw a green rectangle around the ball
        img.draw_cross(max_blob.cx(), max_blob.cy(), color=(0, 255, 0))  # Draw a green cross at the ball's center
        # Draw cross in center of screen
        img.draw_cross(img.width()//2, img.height()//2, size = min(img.width()//5, img.height()//5))
        # Draw distance
        for i in range(len(blobs)):
            img.draw_string(blobs[i][0] - 16, blobs[i][1] - 16, "Distance %d mm" % rect_size_to_distance(blobs[i]))
            #print(rect_size_to_distance(blobs[i])) #debug
            s1.angle(-calculate_pan_angle(max_blob.cx(), image_width_pixels, rect_size_to_distance(blobs[i])))
            s2.angle(-calculate_tilt_angle(max_blob.cy(), image_height_pixels, rect_size_to_distance(blobs[i])))
            p.high() # or p.value(1) to make the pin high (3.3V)
            utime.sleep_ms(300)
            p.low()
            blink_led()
            print(-2*calculate_tilt_angle(max_blob.cy(), image_height_pixels, rect_size_to_distance(blobs[i]))) #debug
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
