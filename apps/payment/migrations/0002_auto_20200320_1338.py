# Generated by Django 3.0.4 on 2020-03-20 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='topup',
            table='payment_topup',
        ),
    ]
