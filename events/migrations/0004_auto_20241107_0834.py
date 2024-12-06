# Generated by Django 2.1.15 on 2024-11-07 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='event_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='event_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
