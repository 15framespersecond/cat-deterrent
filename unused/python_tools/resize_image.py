import os
from PIL import Image 

path = os.getcwd()

def resize(filename):
    img = Image.open(filename)
    w, h = img.size
    if w == 320:
        print(filename, "unchanged")
    else:
        new_img= img.resize((320, 240)) #w = 320 h = 240
        new_img.save(filename)
        print(filename, "resized")
    return

for filename in os.listdir(path):
    if filename == ".gitkeep":
        print(".gitkeep skipped")
    else:
        resize(filename)