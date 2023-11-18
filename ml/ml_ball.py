# Tennis Ball Cascade with distance
# ML example using a Haarcascade. The one loaded here was is for tennis balls taken from 
# https://github.com/radosz99/tennis-ball-detector and convert using cascade_convert.py



import sensor, time, image

lens_mm = 2.8 # Standard Lens.
average_object_height_mm = 64.9 # height of tennis ball
image_height_pixels = 240.0 # QVGA
sensor_h_mm = 2.952 # For OV7725 sensor - see datasheet.
offest_mm = 100.0 # Offset fix...


def rect_size_to_distance(r): # r == (x, y, w, h) -> r[3] == h
    return ((lens_mm * average_object_height_mm * image_height_pixels) / (r[3] * sensor_h_mm)) - offest_mm

# Reset sensor
sensor.reset()

# Sensor settings
sensor.set_contrast(1)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.GRAYSCALE)

# Load Haar Cascade
# By default this will use all stages, lower satges is faster but less accurate.
face_cascade = image.HaarCascade('/cascade_12stages_24dim_0_25far.cascade')
print(face_cascade)

# FPS clock
clock = time.clock()

while (True):
    clock.tick()

    # Capture snapshot
    img = sensor.snapshot()

    # Find objects.
    # Note: Lower scale factor scales-down the image more and detects smaller objects.
    # Higher threshold results in a higher detection rate, with more false positives.
    objects = img.find_features(face_cascade, threshold=0.75, scale_factor=1.25)


    # Draw objects
    for i in range(len(objects)):
        img.draw_rectangle(objects[i])
        img.draw_string(objects[i][0] - 16, objects[i][1] - 16, "Distance %d mm" % rect_size_to_distance(objects[i]))

    img.draw_cross(img.width()//2, img.height()//2, size = min(img.width()//5, img.height()//5))

    # Print FPS.
    # Note: Actual FPS is higher, streaming the FB makes it slower.
    print("FPS %f" % clock.fps())
