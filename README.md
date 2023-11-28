# cat-deterrent
## Intro
This project is effectively a water gun turret designed to track and shoot tennis balls. Ideally, we want to detect cats with the [OpenMv Camera](https://openmv.io/), and have a watergun servo system fire at the cat. For demostration, we are only detecting tennis balls for now. 

## Physical System
The system built for this project is composed a pan/tilt platform with a 3d printed mount water pump taken from a watergun.

## Use
You will need the [OpenMV IDE](https://openmv.io/pages/download) to upload to the camera via USB connection.

- 'system_test.py' is a program to ensure all the functions of the physical system. 

- 'main.py' is the program that tracks a tennis ball and triggers the water gun

Adjust parameters such as threshold_lab, threshold_rbg for the desired object in your desired enviroment. Calibrate distances for your system changing offset_mm.  

## Software
The program first takes a picture of the scene and stores it to memorry. It S




