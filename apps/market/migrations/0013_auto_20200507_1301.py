# Generated by Django 3.0.6 on 2020-05-07 06:01

from django.db import migrations, models
import gdstorage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_auto_20200423_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boughtproofdocument',
            name='value_file',
            field=models.FileField(blank=True, max_length=500, storage=gdstorage.storage.GoogleDriveStorage(), upload_to='files/proof'),
        ),
        migrations.AlterField(
            model_name='boughtproofdocument',
            name='value_image',
            field=models.ImageField(blank=True, max_length=500, storage=gdstorage.storage.GoogleDriveStorage(), upload_to='images/proof'),
        ),
    ]
