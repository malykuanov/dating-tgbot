# Generated by Django 4.0 on 2021-12-11 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_alter_profile_options_alter_profile_age_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.IntegerField(blank=True, null=True, verbose_name='Возраст'),
        ),
    ]
