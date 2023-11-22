# cat-deterrent
## Intro
This project is effectively a water gun turret designed to track and shoot tennis balls. Ideally, we want to detect cats with the [OpenMv Camera](https://openmv.io/), and have a watergun servo system fire at the cat. For demostration, we are only detecting tennis balls for now. 

## Physical System
We have built a pan/tilt system out with the insides of a water gun attatched.

## Software
A haarcasecade was trained using [opencv-haar-classifier-training](https://github.com/mrnugget/opencv-haar-classifier-training) and converted with casecade_convert.py.  'tennis_ballGT' has all the photos used for training. 
## Use
You will need the [OpenMV IDE](https://openmv.io/pages/download) to upload to the camera via USB connection.

- 'system_test.py' is a program to ensure all the functions of the physical system. 

- 'main_tennisball.py' is the program that tracks a tennis ball and triggers the water gun

- 'ml_ball.py' uses a our trained tennis ball Haarcascade to detect the ball, but is not very good

- python_tools are tools to manipluate images for haar classifier training. run in a directory where desired images need to be manipulated

- 'ml_cats.py' uses a our trained cat Haarcasecade to detect cats(need to do still)





