# cat-deterrent
## Intro
This project is effectively a water gun turret. Ideally, we want to detect cats with the [OpenMv Camera]{https://openmv.io/}, and have a watergun servo system fire at the cat. For demostration, we are only detecting tennis balls for now. We are detecting the tennis ball with the OpenMv library were you can set a color threshold to 'find_blobs'. 

## Physical System
We have built a pan/tilt system out with the insides of a water gun attatched. 

## Installation and Use
You will need the [OpenMV IDE]{https://openmv.io/pages/download} to upload to the camera via USB connection.

-'system_test.py' is a program to ensure all the functions of the physical system. 

-'main.py' is the program that tracks an object and triggers the water gun

-'ml_ball.py' uses a tennis ball Haarcascade to detect the ball, but is not very good





