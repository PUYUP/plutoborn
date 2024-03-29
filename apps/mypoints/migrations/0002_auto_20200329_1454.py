# Generated by Django 3.0.4 on 2020-03-29 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('mypoints', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='points',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='points',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
