# Generated by Django 3.2.8 on 2021-11-21 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('equipamentos', '0001_initial'),
        ('capitalcost', '0004_equipmentproject_pressure'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipmentproject',
            name='preference_unity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='equipamentos.equipmentunity'),
        ),
    ]