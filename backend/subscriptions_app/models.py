from django.db import models

from users_app.models import User


class Subscription(models.Model):
    """
    Модель подписок.
    """
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Отслеживаемый автор'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_subscription'
            )
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
