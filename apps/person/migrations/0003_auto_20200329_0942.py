# Generated by Django 3.0.4 on 2020-03-29 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0002_auto_20200329_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='born_date',
            field=models.DateField(blank=True, null=True, verbose_name='Tanggal Lahir'),
        ),
        migrations.AddField(
            model_name='profile',
            name='born_place',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Tempat Lahir'),
        ),
        migrations.AddField(
            model_name='profile',
            name='graduation_year',
            field=models.IntegerField(blank=True, null=True, verbose_name='Tahun Kelulusan'),
        ),
        migrations.AddField(
            model_name='profile',
            name='instagram',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Akun Instagram'),
        ),
        migrations.AddField(
            model_name='profile',
            name='school_origin',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Asal Sekolah'),
        ),
        migrations.AddField(
            model_name='profile',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nomor WhatsApp'),
        ),
    ]
