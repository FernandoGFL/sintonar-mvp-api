from PIL import Image
from io import BytesIO

from django.core.management.base import BaseCommand
from django.db import transaction
from crushonu.apps.authentication.models import UserPhoto
from django.core.files.uploadedfile import InMemoryUploadedFile


def resize_image(image):
    # Carrega a imagem com o PIL
    img = Image.open(image)

    img = img.convert('RGB')

    # Redimensiona a imagem
    img.thumbnail((640, 800))

    file_name = image.name.split('.')[0] + '.jpg'

    # Comprime a imagem
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=60)
    img_file = InMemoryUploadedFile(
        img_io, None, file_name, 'image/jpeg', img_io.getbuffer().nbytes, None)

    return img_file


def save_image(user_photo, file):
    """Salva uma imagem redimensionada e comprimida."""
    # Redimensiona e comprime a imagem usando a função resize_image
    resized_file = resize_image(file)

    # Cria um objeto InMemoryUploadedFile a partir do arquivo redimensionado e comprimido
    file_name = file.name.split('.')[0] + '.jpg'

    # Salva o arquivo redimensionado e comprimido no banco de dados ou no sistema de arquivos
    # (o código abaixo salva o arquivo no sistema de arquivos)
    user_photo.photos.save(file_name, resized_file)
    user_photo.save()


class Command(BaseCommand):
    help = 'Populate database with initial data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Obtém todas as fotos de usuários e redimensiona e comprime cada uma delas
        for user_photo in UserPhoto.objects.all():
            save_image(user_photo, user_photo.photos)
