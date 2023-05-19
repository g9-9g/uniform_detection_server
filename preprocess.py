from PIL import Image, ExifTags
from PIL.Image import Transpose

def autorotate(path):
    try:
        image = Image.open(path)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        oriented_image = None
        if exif[orientation] == 3:
            oriented_image = image.transpose(Transpose.ROTATE_180)
        elif exif[orientation] == 6:
            oriented_image = image.transpose(Transpose.ROTATE_270)
        elif exif[orientation] == 8:
            oriented_image = image.transpose(Transpose.ROTATE_90)

        oriented_image.save(path, quality=95)
        oriented_image.close()
        return True
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        print("No EXIF data found")
        return False

def autoresize(path, new_width = 640, new_height = 640):
    image = Image.open(path)
    (width, height) = image.size
    if width != new_width and height != new_height:
        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        resized_image.save(path, quality=95)
        resized_image.close()
        print("Image resized successfully")
        return True

    return False

def remove_alpha_channel(path):
    image = Image.open(path)

    if image.mode in ['RGBA', 'LA'] or (image.mode == 'P' and 'transparency' in image.info):
        image = image.convert('RGB')
        image.save(path, quality=95)
        print(f"Alpha channel removed")
        return True
    else:
        print("Image does not have an alpha channel. No changes made.")

    return False

def process_images(paths=[]):
    for path in paths:
        remove_alpha_channel(path)
        autorotate(path)
        autoresize(path)
