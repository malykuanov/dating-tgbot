from django.db import models


class User(models.Model):
    chat_id = models.CharField(
        primary_key=True,
        max_length=128,
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
    is_registered = models.BooleanField(
        default=False,
        verbose_name='Анкета зарегистрирована?'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Анкета активна?'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return str(self.user)


class ProfileSearch(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    age = models.CharField(
        max_length=10,
        default='13-100',
        verbose_name='Возраст собеседника'
    )
    sex = models.CharField(
        max_length=1,
        default='F',
        verbose_name='Пол собеседника'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Профиль для поиска'
        verbose_name_plural = 'Профили для поиска'

    def __str__(self):
        return str(self.user)
