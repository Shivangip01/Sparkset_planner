# Generated by Django 2.1.15 on 2024-11-10 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20241107_1009'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='event_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='event_time',
            new_name='end_time',
        ),
        migrations.AddField(
            model_name='booking',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
