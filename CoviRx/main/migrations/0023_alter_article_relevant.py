# Generated by Django 3.2.6 on 2022-04-03 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='relevant',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
