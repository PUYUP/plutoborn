# Generated by Django 3.0.4 on 2020-03-30 01:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('code', models.CharField(max_length=10, verbose_name='Kode Voucher')),
                ('label', models.CharField(max_length=500, verbose_name='Nama Voucher')),
                ('description', models.TextField(blank=True)),
                ('coin_amount', models.BigIntegerField()),
                ('max_usage', models.BigIntegerField(verbose_name='Boleh Digunakan Sebanyak?')),
                ('max_usage_per_user', models.BigIntegerField(verbose_name='Per User Boleh Menggunakan Sebanyak?')),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('finish_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Aktif'), ('inactive', 'Tidak Aktif'), ('expired', 'Expired')], default='active', max_length=255)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vouchers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Voucher',
                'verbose_name_plural': 'Vouchers',
                'db_table': 'market_voucher',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VoucherAcquired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voucher_acquireds', to=settings.AUTH_USER_MODEL)),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voucher_acquireds', to='market.Voucher')),
            ],
            options={
                'verbose_name': 'Voucher Acquired',
                'verbose_name_plural': 'Voucher Acquireds',
                'db_table': 'market_voucher_acquired',
                'abstract': False,
            },
        ),
    ]
