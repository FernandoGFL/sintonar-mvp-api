from PIL import Image
from io import BytesIO

from django.core.management.base import BaseCommand
from django.db import transaction
from crushonu.apps.authentication.models import UserPhoto
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile


def resize_image(image):
    # Pega a extensão do arquivo
    extension = image.name.split('.')[-1].upper()

    if extension == 'JPG':
        extension = 'JPEG'

    # Carrega a imagem com o PIL
    img = Image.open(image)

    # Redimensiona a imagem
    img.thumbnail((640, 800))

    # Comprime a imagem
    img_io = BytesIO()
    img.save(img_io, format=extension, optimize=True, quality=60)
    img_io.seek(0)

    return img_io


def save_image(user_photo, file):
    """Salva uma imagem redimensionada e comprimida."""
    # Redimensiona e comprime a imagem usando a função resize_image
    resized_file = resize_image(file)

    # Cria um objeto InMemoryUploadedFile a partir do arquivo redimensionado e comprimido
    file_name = file.name
    file_content = ContentFile(resized_file.read())
    resized_file = InMemoryUploadedFile(
        file_content, None, file_name, f'image/{file_name.split(".")[-1]}',
        file_content.tell, None
    )

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
