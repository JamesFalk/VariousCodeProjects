import os

def get_images(image_directory='static/PicRoll'):
    return os.listdir(image_directory)