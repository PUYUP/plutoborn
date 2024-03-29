# Generated by Django 3.0.5 on 2020-04-07 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0003_auto_20200329_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('staff', 'Staff'), ('registered', 'Registered')], default='registered', max_length=255),
        ),
        migrations.AlterField(
            model_name='rolecapabilities',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('staff', 'Staff'), ('registered', 'Registered')], max_length=255),
        ),
    ]
