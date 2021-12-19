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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.chat_id)


class City(models.Model):
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Наименование н/п'
    )
    region = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Регион'
    )
    is_basic = models.BooleanField(
        default=True,
        verbose_name='В базовом списке?'
    )

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return str(f'{self.name}, {self.region}')


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
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )
    description = models.CharField(
        max_length=400,
        blank=True,
        verbose_name='О себе'
    )
    avatar = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Фото пользователя'
    )
    is_registered = models.BooleanField(
        default=False,
        verbose_name='Анкета зарегистрирована?'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return str(self.user)
