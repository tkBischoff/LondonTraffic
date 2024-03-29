# Generated by Django 4.2.6 on 2023-10-27 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JamCam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Capture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('image_url', models.CharField(max_length=500)),
                ('video_url', models.CharField(max_length=500)),
                ('jam_cam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='map.jamcam')),
            ],
        ),
    ]
