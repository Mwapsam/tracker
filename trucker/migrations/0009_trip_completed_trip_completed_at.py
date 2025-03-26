# Generated by Django 5.1.7 on 2025-03-26 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trucker", "0008_trip_average_speed_stop"),
    ]

    operations = [
        migrations.AddField(
            model_name="trip",
            name="completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="trip",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
