from api.constants import (EMAIL_MAX_LEN, FIRST_NAME_MAX_LEN,
                           LAST_NAME_MAX_LEN, USERNAME_MAX_LEN)
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    email = models.EmailField(
        verbose_name='e-mail',
        max_length=EMAIL_MAX_LEN,
        unique=True
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_MAX_LEN
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_MAX_LEN
    )

    username = models.CharField(
        verbose_name='username',
        max_length=USERNAME_MAX_LEN,
        unique=True,
        validators=(validate_username,)
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name="unique_follow",
                ordering=['-author_id']
            ),
            models.CheckConstraint(
                check=~models.Q(
                    author=models.F('user')
                ), name='self_subscription'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
