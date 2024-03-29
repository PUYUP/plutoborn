# Generated by Django 3.0.6 on 2020-05-19 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0013_auto_20200507_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='bundle',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bundle',
            name='coin_amount',
            field=models.BigIntegerField(help_text='Jika gratis isi dengan nol.Jika is_free dicentang field ini diabaikan.Berguna jika user tetap ingin beli Bundel free.'),
        ),
    ]
