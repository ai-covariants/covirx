# Generated by Django 3.2.6 on 2021-10-02 19:29

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.DateField(default=django.utils.timezone.now, help_text='The time at which the first visit of the day was recorded')),
                ('session_key', models.CharField(help_text='Django session identifier', max_length=40)),
                ('page_visited', models.CharField(help_text='URL', max_length=40)),
            ],
            options={
                'unique_together': {('session_key', 'page_visited', 'timestamp')},
            },
        ),
    ]
