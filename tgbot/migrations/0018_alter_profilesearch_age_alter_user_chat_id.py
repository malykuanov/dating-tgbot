# Generated by Django 4.0 on 2021-12-31 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0017_alter_profilesearch_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesearch',
            name='age',
            field=models.CharField(default='13-100', max_length=10, verbose_name='Возраст собеседника'),
        ),
        migrations.AlterField(
            model_name='user',
            name='chat_id',
            field=models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='Chat id пользователя'),
        ),
    ]
