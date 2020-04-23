# Generated by Django 3.0.5 on 2020-04-10 23:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tryout', '0014_question_numbering_local'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='theory',
            field=models.ForeignKey(limit_choices_to={'parent__isnull': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='tryout.Theory', verbose_name='Materi'),
        ),
    ]