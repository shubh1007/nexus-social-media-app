# Generated by Django 4.1.5 on 2023-01-25 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_profile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_img',
            field=models.ImageField(default='default-profile-img.png', upload_to='profile_img'),
        ),
    ]