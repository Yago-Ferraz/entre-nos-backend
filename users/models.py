
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None  # Remove username
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'email'  # Agora o login é pelo email
    REQUIRED_FIELDS = []   