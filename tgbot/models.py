from django.db import models


class User(models.Model):
    chat_id = models.IntegerField(
        verbose_name='Chat id пользователя'
    )
    first_name = models.CharField(
        max_length=128,
        verbose_name='Имя пользователя'
    )
    username = models.CharField(
        max_length=64,
        verbose_name='Ник пользователя'
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
