from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAX_LENGTH_FOR_EMAIL


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGTH_FOR_EMAIL,
        verbose_name='Email',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
