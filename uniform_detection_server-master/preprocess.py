from PIL import Image, ExifTags
from PIL.Image import Transpose

def autorotate(path):
    try:
        image = Image.open(path)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        print(exif[orientation])

        # exif = image._getexif()
        oriented_image = None
        if exif[orientation] == 3:
            oriented_image = image.transpose(Transpose.ROTATE_180)
        elif exif[orientation] == 6:
            oriented_image = image.transpose(Transpose.ROTATE_270)
        elif exif[orientation] == 8:
            oriented_image = image.transpose(Transpose.ROTATE_90)

        oriented_image.save(path)
        # oriented_image.show()
        oriented_image.close()
        return True
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return False
        pass

def autoresize(path, new_width = 640, new_height = 640):
    image = Image.open(path)
    (width, height) = image.size
    if width != new_width and height != new_height:
        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        resized_image.save(path, quality=100)
        resized_image.close()
        return True

    return False
