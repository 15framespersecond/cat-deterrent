import os
from PIL import Image 
  

path = os.getcwd()

def png_to_jpg(filename):
    img_png = Image.open(filename)
    if filename.endswith(".png")==1:
        tmp = filename.removesuffix(".png")
        newname = tmp + ".jpg"
        img_png.save(newname)
        print(filename, "format changed to:", newname)
        os.remove(filename)
    else:
        print(filename, "format unchanged")
    return 

#function to rename if .JPG is in all caps 
def rename(filename):
    if filename.endswith(".JPG") == 1:
        tmp = filename.removesuffix(".JPG")
        data = tmp + ".jpg"
        print("renamed")
    else:
        data = filename
    
    return os.rename(filename, data)

for filename in os.listdir(path):
    if filename == ".gitkeep":
        print(".gitkeep skipped")
    else:
        png_to_jpg(filename)