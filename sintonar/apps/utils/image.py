from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile


def resize_image(image_instance):
    # Load the image with PIL
    image = Image.open(image_instance)
    image = image.convert('RGB')

    # Resize the image
    image.thumbnail((640, 800))

    file_name = image_instance.name.split('.')[0] + '.jpg'

    # Compress the image
    image_io = BytesIO()
    image.save(image_io, format='JPEG', quality=75)
    resized_image = InMemoryUploadedFile(
        file=image_io,
        field_name=None,
        name=file_name,
        content_type='image/jpeg',
        size=image_io.getbuffer().nbytes,
        charset=None
    )

    return resized_image
