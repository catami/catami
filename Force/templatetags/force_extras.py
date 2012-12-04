import os
import Image
from django.template import Library

register = Library()

def scale(max_x, size):
    " size is a tuple: (image_x,image_y) "
    x, y = size
    new_y = (float(max_x) / x) * y
    return (int(max_x), int(new_y))

def thumbnail(file, size='150x150'):
    """
    Examples:
    <img src="object.src.url" alt="original image" />
    <img src="object.image.src|thumbnail" alt="image resized to default 80x60 format" />

    <img src="object.image.src|thumbnail:"200x150"
         alt="image resized to 200x150, cropped at 150 height if incorrect aspect ratio" />

    <img src="object.image.src|thumbnail:"200x0"
         alt="image scaled to 250 width, height not croppped / adjusted if incorrect aspect ratio" />
    """
    if file:
        # get size params
        x, y = [int(x) for x in size.split('x')]
        #
        # basename, format = file.path.rsplit('.', 1)
        # baseurl, _format = file.url.rsplit('.', 1)
        # new_filename = basename + '_' + size + '.jpg'
        # new_url = baseurl + '_' + size + '.jpg'

        # # if the new image wasn't already resized..
        # if not os.path.exists(new_filename):
        #     image = Image.open(file.path)

        #     # scale image
        #     # image.size returns (a,tuple)
        #     image_x, image_y = scale(x,image.size)
        #     # convert to RGB
        #     if image.mode not in ("L", "RGB"):
        #         image = image.convert("RGB")
        #     # 'resize'
        #     image.thumbnail([image_x, image_y], Image.ANTIALIAS)
        #     # crop if/to max_height setting
        #     if image_y > image_x & y is not 0:
        #         # crop image height
        #         left, top = 0, 0
        #         box = (left, top, left+x, top+y)
        #         image = image.crop(box)
        #     image.save(new_filename, 'JPEG', quality=70)
        # return new_url
    return ''

register.filter(thumbnail)