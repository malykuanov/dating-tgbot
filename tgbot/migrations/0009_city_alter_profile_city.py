# Generated by Django 4.0 on 2021-12-15 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0008_profile_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Наименование н/п')),
                ('region', models.CharField(blank=True, max_length=200, verbose_name='Регион')),
                ('is_basic', models.BooleanField(default=True, verbose_name='В базовом списке?')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.AlterField(
            model_name='profile',
            name='city',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='tgbot.city'),
        ),
    ]