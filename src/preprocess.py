from PIL import Image, ExifTags
from PIL.Image import Transpose

def autorotate(image):
    try:
       
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

        return oriented_image
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        print("No EXIF data found")
        return image

def autoresize(image, new_width = 640, new_height = 640):

    (width, height) = image.size
    if width != new_width and height != new_height:
        resized_image = image.resize((new_width, new_height))

        print("Image resized successfully")
        return resized_image

    return image

def remove_alpha_channel(image):

    if image.mode in ['RGBA', 'LA'] or (image.mode == 'P' and 'transparency' in image.info):
        bimage = image.convert('RGB')
        print(f"Alpha channel removed")
        return bimage
    else:
        print("Image does not have an alpha channel. No changes made.")

    return image

def process_images(paths=[]):
    for path in paths:
        image = Image.open(path)
        image = remove_alpha_channel(autorotate(autoresize(image)))
        # image.show()
        image.save(path, quality = 95)
        image.close()

