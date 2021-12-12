from django.db import models


class User(models.Model):
    chat_id = models.IntegerField(
        primary_key=True,
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

    def __str__(self):
        return str(self.chat_id)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Имя'
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Возраст'
    )
    sex = models.CharField(
        max_length=1,
        blank=True,
        verbose_name='Пол'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Город'
    )
    description = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='О себе'
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return str(self.user)
