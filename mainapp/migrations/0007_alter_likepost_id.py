# Generated by Django 4.1.5 on 2023-01-25 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_likepost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likepost',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
