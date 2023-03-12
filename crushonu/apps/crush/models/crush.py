from django.db import models
from django.contrib.auth import get_user_model

from uuid import uuid4


User = get_user_model()


class Crush(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_from = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_from')
    user_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_to')
    kiss = models.BooleanField(default=False)
    match = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crush'
