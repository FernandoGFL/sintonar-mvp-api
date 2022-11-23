from crushonu.apps.authentication.models import UserPhoto

from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(pre_delete, sender=UserPhoto)
def delete_user_photo_file(sender, instance, **kwargs):
    instance.photo.delete(False)