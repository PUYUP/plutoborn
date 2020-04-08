# Generated by Django 3.0.4 on 2020-03-20 08:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0002_auto_20200320_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('transaction_type', models.CharField(choices=[('topup', 'Top Up'), ('used', 'Used')], default='topup', max_length=255)),
                ('amount', models.BigIntegerField()),
                ('current_amount', models.BigIntegerField(blank=True, default=0, null=True)),
                ('topup', models.ForeignKey(blank=True, limit_choices_to={'is_used': False, 'status': 'paid'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coins', to='payment.TopUp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coins', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Coin',
                'verbose_name_plural': 'Coins',
                'db_table': 'payment_coin',
                'ordering': ['-date_created'],
                'abstract': False,
            },
        ),
    ]
