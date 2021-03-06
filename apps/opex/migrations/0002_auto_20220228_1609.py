# Generated by Django 3.2.8 on 2022-02-28 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('capex', '0001_initial'),
        ('opex', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashFlow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(blank=True, null=True)),
                ('descricao', models.CharField(max_length=100)),
                ('valor', models.FloatField()),
                ('data', models.DateField()),
            ],
            options={
                'db_table': 'cash_flow',
            },
        ),
        migrations.CreateModel(
            name='Opex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fixed_costs', models.FloatField(blank=True, null=True)),
                ('general_expenses', models.FloatField(blank=True, null=True)),
                ('direct_costs', models.FloatField(blank=True, null=True)),
                ('crm', models.FloatField(blank=True, null=True)),
                ('cwt', models.FloatField(blank=True, null=True)),
                ('cut', models.FloatField(blank=True, null=True)),
                ('col', models.FloatField(blank=True, null=True)),
                ('com', models.FloatField(blank=True, null=True)),
                ('fci', models.FloatField(blank=True, null=True)),
                ('depreciation', models.FloatField(blank=True, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capex.capexproject')),
            ],
            options={
                'db_table': 'opex_factors',
            },
        ),
        migrations.CreateModel(
            name='OpexAuxiliateFactor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crm', models.FloatField(default=1.23)),
                ('cwt', models.FloatField(default=1.23)),
                ('cut', models.FloatField(default=1.23)),
                ('col', models.FloatField(default=2.76)),
                ('fci', models.FloatField(default=0.18)),
                ('working_capital_a', models.FloatField(default=0.1)),
                ('working_capital_b', models.FloatField(default=0.1)),
                ('working_capital_c', models.FloatField(default=0.1)),
                ('construction_period', models.IntegerField(blank=True, default=0, null=True)),
                ('project_life', models.IntegerField(blank=True, default=0, null=True)),
                ('year1', models.FloatField(blank=True, default=1, null=True)),
                ('year2', models.FloatField(blank=True, default=0, null=True)),
                ('year3', models.FloatField(blank=True, default=0, null=True)),
                ('year4', models.FloatField(blank=True, default=0, null=True)),
                ('year5', models.FloatField(blank=True, default=0, null=True)),
                ('capex_source', models.CharField(blank=True, max_length=25, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capex.capexproject')),
            ],
            options={
                'db_table': 'opex_auxiliar_factor',
            },
        ),
        migrations.CreateModel(
            name='OpexNonEssentialFactor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('value', models.FloatField(default=1.0)),
                ('unity', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'opex_nonessential_factors',
            },
        ),
        migrations.DeleteModel(
            name='HistoricoFluxoCaixa',
        ),
    ]
