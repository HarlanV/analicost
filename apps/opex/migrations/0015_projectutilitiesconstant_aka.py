# Generated by Django 3.2.8 on 2022-03-01 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opex', '0014_rename_cost_projectutilitiesconstant_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectutilitiesconstant',
            name='aka',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]