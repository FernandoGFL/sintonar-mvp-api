from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from crushonu.apps.authentication.models import UserPhoto
from crushonu.apps.utils.image import resize_image


def save_image(user_photo, file):
    """Salva uma imagem redimensionada e comprimida."""
    # Redimensiona e comprime a imagem usando a função resize_image
    resized_file = resize_image(file)

    # Cria um objeto InMemoryUploadedFile a partir do arquivo redimensionado e comprimido
    file_name = file.name.split('.')[0] + '.jpg'
    file_content = ContentFile(resized_file.read())
    resized_file = InMemoryUploadedFile(
        file_content, None, file_name, 'image/jpeg',
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
