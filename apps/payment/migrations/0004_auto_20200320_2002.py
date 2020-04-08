# Generated by Django 3.0.4 on 2020-03-20 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_coin'),
    ]

    operations = [
        migrations.AddField(
            model_name='topup',
            name='order_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='coin',
            name='transaction_type',
            field=models.CharField(choices=[('in', 'Koin Masuk'), ('out', 'Koin Keluar')], default='in', max_length=255),
        ),
    ]
