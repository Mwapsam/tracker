# Generated by Django 5.1.7 on 2025-03-15 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trucker", "0002_alter_driver_user_alter_dutystatus_log_entry"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="driver",
            name="carrier",
        ),
        migrations.AddField(
            model_name="driver",
            name="carriers",
            field=models.ManyToManyField(blank=True, to="trucker.carrier"),
        ),
    ]
