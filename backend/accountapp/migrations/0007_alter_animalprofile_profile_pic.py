# Generated by Django 4.2.9 on 2024-08-10 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accountapp", "0006_animalprofile_profile_pic_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animalprofile",
            name="profile_pic",
            field=models.ImageField(blank=True, null=True, upload_to="profile_pics/"),
        ),
    ]
