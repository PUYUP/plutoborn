# Generated by Django 3.0.4 on 2020-03-30 09:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tryout', '0011_auto_20200330_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramStudy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Prodi',
                'verbose_name_plural': 'Prodi',
                'db_table': 'tryout_program_study',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='simulation',
            name='program_study',
            field=models.ManyToManyField(blank=True, related_name='simulations', to='tryout.ProgramStudy'),
        ),
    ]
