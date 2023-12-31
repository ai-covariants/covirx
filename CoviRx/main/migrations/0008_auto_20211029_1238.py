# Generated by Django 3.2.6 on 2021-10-29 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20211029_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='adddrug',
            name='indication',
            field=models.CharField(blank=True, max_length=50, verbose_name='Indication'),
        ),
        migrations.AddField(
            model_name='adddrug',
            name='indication1',
            field=models.CharField(blank=True, max_length=50, verbose_name='Indication(1)'),
        ),
        migrations.AddField(
            model_name='adddrug',
            name='researchArea',
            field=models.CharField(blank=True, max_length=100, verbose_name='Research Area'),
        ),
        migrations.AddField(
            model_name='adddrug',
            name='status',
            field=models.CharField(blank=True, max_length=25, verbose_name='Status'),
        ),
    ]
