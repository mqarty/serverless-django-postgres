import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    sid = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
        verbose_name="secure id",
        unique=True,
    )


# Enforce user fields to be required
get_user_model()._meta.get_field("email").blank = False  # noqa
