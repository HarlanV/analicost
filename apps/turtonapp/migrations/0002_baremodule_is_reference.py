# Generated by Django 3.2.8 on 2021-11-11 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turtonapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='baremodule',
            name='is_reference',
            field=models.BooleanField(blank=True, default=0),
        ),
    ]
