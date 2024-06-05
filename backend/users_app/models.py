from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users_app.constants import (EMAIL_MAX_LENGTH,
                                 FIRST_NAME_LENGTH,
                                 LAST_NAME_LENGTH,
                                 PASSWORD_MAX_LENGTH,
                                 USERNAME_MAX_LENGTH)


class User(AbstractUser):
    """
    Используется стандартная модель Пользователя.
    Переопределены условия работы полей и добавлены ограничения.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        blank=False,
        unique=True,
        null=False,
        validators=([RegexValidator(regex=r'^[\w.@+-]+$')]),
        verbose_name='логин',
        help_text=('Логин, должен содержать только буквы,'
                   ' точку, знаки плюса, дефиса и @.'
                   f' Ограничение в {USERNAME_MAX_LENGTH} символов.')
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        blank=False,
        unique=True,
        null=False,
        verbose_name='e-mail',
        help_text=f'Ограничение в {EMAIL_MAX_LENGTH} символов.'
    )
    password = models.CharField(
        max_length=PASSWORD_MAX_LENGTH,
        blank=False,
        null=False,
        verbose_name='пароль',
        help_text=('Пароль должен содержать не менее 8 символов. Состоять'
                   ' из цифр, одной заглавной латинской буквы'
                   ', одной прописной латинской буквы.'
                   f'Ограничение в {PASSWORD_MAX_LENGTH} символов.')
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_LENGTH,
        blank=False,
        null=False,
        verbose_name="имя",
        help_text=f'Имя. Ограничение в {FIRST_NAME_LENGTH} символов.'
    )
    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        blank=False,
        null=False,
        verbose_name="фамилия",
        help_text=f'Фамилия. Ограничение в {LAST_NAME_LENGTH} символов.'
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
