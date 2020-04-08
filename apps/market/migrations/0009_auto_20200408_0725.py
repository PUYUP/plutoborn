# Generated by Django 3.0.5 on 2020-04-08 00:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0008_auto_20200407_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliatecommission',
            name='affiliator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commission_affiliators', to=settings.AUTH_USER_MODEL),
        ),
    ]
