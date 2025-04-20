# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def get_image_date_taken(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    return value
    except Exception as e:
        pass
    return None

def get_video_date_taken(file_path):
    try:
        parser = createParser(file_path)
        if not parser:
            return None
        with parser:
            metadata = extractMetadata(parser)
        if metadata and metadata.has("creation_date"):
            return metadata.get("creation_date")
    except Exception:
        pass
    return None

def list_dates_taken(root_folder):
    supported_images = {'.jpg', '.jpeg', '.png', '.heic', '.tiff'}
    supported_videos = {'.mp4', '.mov', '.avi', '.mkv', '.3gp', '.mts'}

    for root, _, files in os.walk(root_folder):
        for name in files:
            file_path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()

            date_taken = None
            if ext in supported_images:
                date_taken = get_image_date_taken(file_path)
            elif ext in supported_videos:
                date_taken = get_video_date_taken(file_path)

            print(f"{file_path} -> {date_taken or 'No date found'}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    #date_taken =  get_image_date_taken('C:/Temp4/IMG_5481.JPEG')
    #date_taken =  get_image_date_taken('C:/Temp4/ana_i_broens.JPEG') # (None)
    #print(date_taken)

    folder = 'C:/Temp4'
    list_dates_taken(folder)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
