# Generated by Django 3.2.6 on 2021-10-29 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_drug_phase'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddDrug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drugName', models.TextField(blank=True)),
                ('drugFormula', models.TextField(blank=True)),
            ],
        ),
    ]
