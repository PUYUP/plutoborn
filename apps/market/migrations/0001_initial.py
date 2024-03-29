# Generated by Django 3.0.4 on 2020-03-21 08:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tryout', '0002_auto_20200321_1534'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('label', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('coin_amount', models.BigIntegerField()),
                ('status', models.CharField(choices=[('published', 'Terbit'), ('draft', 'Konsep')], default='published', max_length=255)),
                ('packet', models.ManyToManyField(limit_choices_to={'status': 'published'}, to='tryout.Packet')),
            ],
            options={
                'verbose_name': 'Bundel',
                'verbose_name_plural': 'Bundel',
                'db_table': 'market_bundle',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bought',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boughts', to='market.Bundle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boughts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dibeli',
                'verbose_name_plural': 'Dibeli',
                'db_table': 'market_bought',
                'abstract': False,
            },
        ),
    ]
