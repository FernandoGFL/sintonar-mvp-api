from crushonu.apps.authentication.models import (
    UserPhoto,
    UserConfirm
)
from crushonu.apps.authentication.tasks import task_send_email

from rest_framework.reverse import reverse

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver


@receiver(pre_delete, sender=UserPhoto)
def delete_user_photo_file(sender, instance, **kwargs):
    instance.photo.delete(False)


@receiver(post_save, sender=UserConfirm)
def send_email_confirmation(sender, instance, created, **kwargs):
    if created:
        url = reverse(
            'user_confirm',
            kwargs={
                'uuid': instance.identification_code
            }
        )

        data = {
            "name": instance.user.first_name,
            "link": "http://localhost:8000" + url
        }

        task_send_email.delay(
            subject="Confirmação de email",
            to=instance.user.email,
            template="authentication/email_confirmation.html",
            data=data
        )
