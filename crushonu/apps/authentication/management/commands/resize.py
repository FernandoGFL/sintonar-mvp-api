from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile

from crushonu.apps.authentication.models import UserPhoto
from PIL import Image
from io import BytesIO


Image.MAX_IMAGE_PIXELS = None


def resize_image(image_instance):
    img = Image.open(image_instance)
    img = img.convert('RGB')

    # Redimensiona a imagem
    img.thumbnail((640, 800))
    file_name = image_instance.name.split('.')[0] + '.jpg'

    img_io = BytesIO()

    img.save(img_io, format='JPEG', quality=75)

    resized_image = InMemoryUploadedFile(
        file=img_io,
        field_name=None,
        name=file_name,
        content_type='image/jpeg',
        size=img_io.getbuffer().nbytes,
        charset=None
    )

    return resized_image


def save_image(user_photo, file):
    """Salva uma imagem redimensionada e comprimida."""
    # Redimensiona e comprime a imagem usando a função resize_image

    try:

        resized_file = resize_image(file)

        # Cria um objeto InMemoryUploadedFile a partir do arquivo redimensionado e comprimido
        file_name = file.name.split('.')[0] + '.jpg'

        # Salva o arquivo redimensionado e comprimido no banco de dados ou no sistema de arquivos
        # (o código abaixo salva o arquivo no sistema de arquivos)
        user_photo.photos.save(file_name, resized_file)
        user_photo.save()
    except:
        user_photo.photos.delete()


class Command(BaseCommand):
    help = 'Populate database with initial data'

    @ transaction.atomic
    def handle(self, *args, **kwargs):
        # Obtém todas as fotos de usuários e redimensiona e comprime cada uma delas
        for user_photo in UserPhoto.objects.all():
            user_photo.photos.open()
            save_image(user_photo, user_photo.photos)
