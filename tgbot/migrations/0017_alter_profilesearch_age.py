# Generated by Django 4.0 on 2021-12-25 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0016_remove_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesearch',
            name='age',
            field=models.CharField(default='12-100', max_length=10, verbose_name='Возраст собеседника'),
        ),
    ]
