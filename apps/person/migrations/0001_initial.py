# Generated by Django 3.0.4 on 2020-03-26 05:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import utils.generals
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleCapabilities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('role', models.TextField(choices=[('admin', 'Admin'), ('staff', 'Staff'), ('registered', 'Registered')])),
                ('permissions', models.ManyToManyField(related_name='role_capabilities', to='auth.Permission')),
            ],
            options={
                'verbose_name': 'Role Capability',
                'verbose_name_plural': 'Role Capabilities',
                'db_table': 'person_role_capabilities',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('role', models.TextField(choices=[('admin', 'Admin'), ('staff', 'Staff'), ('registered', 'Registered')], default='registered')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'db_table': 'person_role',
                'ordering': ['-user__date_joined'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('biography', models.TextField(blank=True, null=True)),
                ('picture', models.ImageField(blank=True, max_length=500, null=True, upload_to='d:\\PROGRAMS\\DJANGO3\\tombolajaib\\media/images/user')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'db_table': 'person_profile',
                'ordering': ['-user__date_joined'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('date_expired', models.DateTimeField(blank=True, editable=False, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('telephone', models.CharField(blank=True, max_length=14, null=True)),
                ('otp_hash', models.CharField(max_length=255)),
                ('otp_code', models.CharField(max_length=255)),
                ('attempt_allowed', models.IntegerField(default=3)),
                ('attempt_used', models.IntegerField(default=0)),
                ('is_used', models.BooleanField()),
                ('is_expired', models.BooleanField(default=False)),
                ('identifier', models.SlugField(choices=[('email_validation', 'Email Validation'), ('change_email_validation', 'Change Email Validation'), ('telephone_validation', 'Telephone Validation'), ('change_telephone_validation', 'Change Telephone Validation'), ('register_validation', 'Register Validation')], max_length=128, null=True, validators=[django.core.validators.RegexValidator(message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit.", regex='^[a-zA-Z_][0-9a-zA-Z_]*$'), utils.generals.non_python_keyword])),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='otps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'OTP Code',
                'verbose_name_plural': 'OTP Codes',
                'db_table': 'person_otpcode',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('telephone', models.CharField(blank=True, max_length=14, null=True)),
                ('email_verified', models.BooleanField(default=False, null=True)),
                ('telephone_verified', models.BooleanField(default=False, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Account',
                'verbose_name_plural': 'Accounts',
                'db_table': 'person_account',
                'ordering': ['-user__date_joined'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='rolecapabilities',
            constraint=models.UniqueConstraint(fields=('role',), name='unique_role'),
        ),
    ]
