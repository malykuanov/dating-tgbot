# Generated by Django 4.0 on 2021-12-12 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0005_rename_user_profile_profile_user_remove_user_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='sex',
            field=models.CharField(blank=True, max_length=1, verbose_name='Пол'),
        ),
    ]