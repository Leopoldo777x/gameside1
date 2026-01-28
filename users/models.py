import uuid

from django.conf import settings
from django.db import models


class Token(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='token', on_delete=models.CASCADE
    )
    key = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
