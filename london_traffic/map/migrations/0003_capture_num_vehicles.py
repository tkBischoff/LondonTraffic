# Generated by Django 4.2.6 on 2023-10-27 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_alter_jamcam_name_alter_capture_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='capture',
            name='num_vehicles',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
