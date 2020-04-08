# Generated by Django 3.0.4 on 2020-03-22 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tryout', '0005_auto_20200322_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='choice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='tryout.Choice'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='tryout.Question'),
        ),
    ]
