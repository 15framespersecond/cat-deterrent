import sensor
import image
import time
import ustruct
import pyb

# Class to store the last 5 frames
class BackgroundBuffer:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.buffer = []
        self.background = image.Image(size=(width // scale, height // scale))

    def add_frame(self, frame):
        self.buffer.append(frame.copy())
        if len(self.buffer) > 5:
            self.buffer.pop(0)

    # Updates background by taking a weighted average of the new frame and previous background
    def update_get_background(self):
        for i in range(len(self.background.get_data())):
            self.background.get_data()[i] = (
                self.background.get_data()[i] // 3
            ) * 2 + self.buffer[0].get_data()[i] // 3
        return self.background


# Object that processes frames for background subtraction
class BackgroundSubtractor:
    def __init__(self, processing_scale, uart, yolo: bool):
        self.PROCESSING_SCALE = processing_scale
        self.uart = uart
        self.yolo = yolo

        if yolo:
            # Implement YOLO model loading for OpenMV if available
            pass

        # Determines frame dimensions
        sensor.reset()
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        sensor.skip_frames(time=2000)
        frame = sensor.snapshot()
        frame_shape = frame.size()
        self.height = frame_shape[1]
        self.width = frame_shape[0]

        # Initializes background buffer
        self.background_buffer = BackgroundBuffer(
            self.width, self.height, self.PROCESSING_SCALE
        )

        # Presents laser coordinates to be the middle of the frame
        self.laser_coordinates = (self.height // 2, self.width // 2)

        # Switch variable for calibration
        self.calibrated = False

    def box_label(self, image, box, label="", color=(128, 128, 128), txt_color=(255, 255, 255)):
        # Implement box_label for OpenMV
        pass

    def plot_bboxes(self, image, boxes, labels=[], colors=[], score=True, conf=None):
        # Implement plot_bboxes for OpenMV
        pass

    # Processes frame subtraction and determines bounding box for the biggest contour found
    # Sends coordinates of the center of the box to the Arduino
    def update(self):
        # Get frame from camera
        unprocessed_frame = sensor.snapshot()

        # Case for YOLO algorithm
        if self.yolo:
            # Implement YOLO processing for OpenMV
            pass
        # Case for background subtraction algorithm
        else:
            # Read and process frame with flip, resize, grayscale, and Gaussian blur
            frame = unprocessed_frame.copy()
            frame = frame.resize(
                width=self.width // self.PROCESSING_SCALE,
                height=self.height // self.PROCESSING_SCALE,
            )
            frame = frame.to_grayscale(copy=True)
            frame.gaussian(5)

            # Updates background buffer, add mask to subtracted frame
            self.background_buffer.add_frame(frame)
            foreground = self.background_buffer.update_get_background().subtract(frame)
            mask = foreground.threshold(15, invert=True)

            # Check if turret is finished calibrating yet
            if not self.calibrated:
                self.check_calibration()
            else:
                # Find biggest blob and its bounding box
                blobs = mask.find_blobs()
                if blobs:
                    biggest_blob = max(blobs, key=lambda b: b.pixels())
                    if biggest_blob.pixels() > 800:
                        x, y, w, h = biggest_blob.rect()
                        x, y, w, h = (
                            x * self.PROCESSING_SCALE,
                            y * self.PROCESSING_SCALE,
                            w * self.PROCESSING_SCALE,
                            h * self.PROCESSING_SCALE,
                        )
                        unprocessed_frame.draw_rectangle((x, y, w, h), color=(0, 255, 0))
                        # Calculate center of bounding box
                        self.laser_coordinates = (y + h // 2, x + w // 2)
                # Send updated coordinates to Arduino
                self.send_laser_coordinates()

            unprocessed_frame.draw_image(mask, x=0, y=0)
            unprocessed_frame.compress(quality=90)
            unprocessed_frame.draw_string(0, 0, "Webcam", color=(255, 255, 255))

            # Display the processed image
            sensor.flush()

    # Checks if the Arduino has sent the byte b'1' which means it has finished calibrating
    def check_calibration(self):
        data = self.uart.read(1)
        if data == b'1':
            self.calibrated = True

    # Sends laser coordinates to Arduino
    def send_laser_coordinates(self):
        self.uart.write(("x" + str(self.laser_coordinates[1]) + ">").encode())
        self.uart.write(("y" + str(self.laser_coordinates[0]) + ">").encode())

    # Groups byte data sent from Arduino and prints it for debugging purposes
    def receive_data(self):
        word = ""
        while self.uart.any():
            char = self.uart.read(1).decode()
            word += char
        print(word)


# Initialize the UART (change the UART port and baudrate accordingly)
uart = pyb.UART(3, 115200)
background_subtractor = BackgroundSubtractor(4, uart, yolo=False)

while True:
    background_subtractor.update()
    background_subtractor.receive_data()
    time.sleep(100)

