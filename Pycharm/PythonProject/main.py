# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from PIL import Image
from PIL.ExifTags import TAGS

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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    folder = 'C:/Temp4/IMG_5481.JPEG'
    date_taken = get_image_date_taken(folder)
    print(date_taken)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
