from crushonu.apps.authentication.models import (
    UserPhoto,
    UserConfirm
)
from crushonu.apps.authentication.tasks import task_send_email

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver


@receiver(pre_delete, sender=UserPhoto)
def delete_user_photo_file(sender, instance, **kwargs):
    instance.photo.delete(False)


@receiver(post_save, sender=UserConfirm)
def send_email_confirmation(sender, instance, created, **kwargs):
    if created:
        data = {
            "name": instance.user.first_name,
            "link": f"http://localhost:8000/authentication/user-confirm/{instance.identification_code}/"
        }

        task_send_email.delay(
            subject="Confirmação de email",
            to=instance.user.email,
            template="authentication/email_confirmation.html",
            data=data
        )
