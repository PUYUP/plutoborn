import itertools

from django import forms
from django.db.models import Prefetch, Q
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from utils.generals import get_model
from apps.person.utils.constant import SELECT_ROLES, REGISTERED

username_validator = UnicodeUsernameValidator()
User = get_user_model()
Role = get_model('person', 'Role')
RoleCapabilities = get_model('person', 'RoleCapabilities')
Account = get_model('person', 'Account')
OTPCode = get_model('person', 'OTPCode')

try:
    _SELECT_ROLES = SELECT_ROLES
except NameError:
    _SELECT_ROLES = list()


try:
    _REGISTERED = REGISTERED
except NameError:
    _REGISTERED = list()


class UserChangeFormExtend(UserChangeForm):
    """ Override user Edit form """
    email = forms.EmailField(max_length=254, help_text=_(
        "Required. Inform a valid email address."))
    role = forms.MultipleChoiceField(
        choices=_SELECT_ROLES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text=_("Select roles for user."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial =  list(self.instance.roles.all().values_list('role', flat=True))

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        username = self.cleaned_data.get('username', None)

        # Make user email filled
        if email:
            # Validate each account has different email
            if User.objects.filter(email=email).exclude(
                    username=username).exists():
                raise forms.ValidationError(_('Email has been used.'))
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role', None)
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        roles = self.cleaned_data.get('role', None)
        permissions_removed = list()
        permissions_add = list()
        permissions_current = user.user_permissions.all()
        capabilities = RoleCapabilities.objects \
            .prefetch_related(Prefetch('permissions'))

        # REMOVE ROLES
        roles_removed = user.roles.exclude(role__in=roles)
        if roles_removed.exists():
            capabilities = capabilities.filter(role__in=roles_removed.values('role'))
            permissions = [list(item.permissions.all()) for item in capabilities]
            permissions_removed = list(set(itertools.chain.from_iterable(permissions)))
            roles_removed.delete()

        # ADD ROLES
        if roles:
            roles_created = list()
            roles_initial = list(user.roles.values_list('role', flat=True))
            roles_new = list(set(roles) ^ set(roles_initial))

            for role in roles_new:
                role_obj = user.roles.model(user_id=user.id, role=role)
                roles_created.append(role_obj)

            if roles_created:
                user.roles.model.objects.bulk_create(roles_created)

            capabilities = capabilities.filter(role__in=user.roles.all().values('role'))
            permissions = [list(item.permissions.all()) for item in capabilities]
            permissions_add = list(set(itertools.chain.from_iterable(permissions)))

        # Compare current with new permissions
        # If has different assign that to user
        if permissions_current:
            add_diff = list(set(permissions_add) & set(permissions_current))
            if add_diff:
                add_diff = list(set(permissions_add) ^ set(add_diff))
        else:
            add_diff = list(set(permissions_add))

        if add_diff and permissions_add:
            user.user_permissions.add(*list(add_diff))

        # Compare current with old permissions
        # If has different remove that
        removed_diff = list(set(permissions_add) ^ set(permissions_removed))
        if removed_diff and permissions_removed:
            diff = set(removed_diff) & set(permissions_removed)
            user.user_permissions.remove(*list(diff))

        return user


class UserCreationFormExtend(UserCreationForm):
    """ Override user Add form """
    email = forms.EmailField(max_length=254, help_text=_(
        "Required. Inform a valid email address."))
    role = forms.MultipleChoiceField(
        choices=_SELECT_ROLES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text=_("Select roles for user."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = _REGISTERED

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        username = self.cleaned_data.get('username', None)

        # Make user email filled
        if email:
            # Validate each account has different email
            if User.objects.filter(email=email).exclude(
                    username=username).exists():
                raise forms.ValidationError(
                    _('Email has been used.'),
                    code='email_used',
                )
        return email

    def save(self, commit=True):
        user = super().save(commit=True)
        if commit:
            user.save()

        # ADD ROLES
        roles = self.cleaned_data.get('role', None)
        if roles:
            roles_created = list()
            roles_initial = list(user.roles.values_list('role', flat=True))
            roles_new = list(set(roles) - set(roles_initial))

            for role in roles_new:
                role_obj = user.roles.model(user_id=user.id, role=role)
                roles_created.append(role_obj)

            if roles_created:
                user.roles.model.objects.bulk_create(roles_created)
        
            capabilities_objs = RoleCapabilities.objects \
                .prefetch_related(Prefetch('permissions')) \
                .filter(role__in=user.roles.all().values('role'))
            permission_objs = [list(item.permissions.all()) for item in capabilities_objs]
            permission_objs_unique = list(set(itertools.chain.from_iterable(permission_objs)))
            user.user_permissions.add(*permission_objs_unique)
        return user


# Before user register check email
class BoardingForm(forms.Form):
    email = forms.EmailField(label=_("Alamat Email"), max_length=100)

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            Account.objects.get(email=email, email_verified=True)
            raise forms.ValidationError(_("Email has used."))
        except ObjectDoesNotExist:
            return email


# Lets verify OTP Code
class VerifyForm(forms.Form):
    otp_code = forms.CharField(label=_("Kode OTP"), max_length=6)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_otp_code(self):
        otp_code = self.cleaned_data['otp_code']
        identifier = 'register_boarding'

        try:
            otp_hash = self.request.session['otp_hash']
        except KeyError:
            otp_hash = None

        try:
            email = self.request.session['email']
        except KeyError:
            email = None

        try:
            otp = OTPCode.objects.get(
                Q(email=email) & Q(identifier=identifier) & Q(otp_hash=otp_hash)
                | Q(otp_code=otp_code), Q(is_used=False), Q(is_expired=False))
        except ObjectDoesNotExist:
            raise forms.ValidationError(_("OTP Code invalid!"))

        try:
            otp.validate(otp_code=otp_code)
        except ValidationError as e:
            raise forms.ValidationError(_(''.join(e.messages)))
        return otp_code


# Lets create user data
class SignupForm(forms.Form):
    full_name = forms.CharField(label=_("Nama Lengkap"))
    username = forms.CharField(label=_("Username"), validators=[username_validator])
    email = forms.EmailField(label=_("Alamat Email"), widget=forms.EmailInput)
    password1 = forms.CharField(label=_("Kata Sandi"), validators=[validate_password], widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Ulangi Kata Sandi"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        email = self.request.session.get('email', False)
        if email:
            self.fields['email'].widget.attrs['readonly'] = True

    def clean_username(self):
        email = self.request.session.get('email', False)
        username = self.cleaned_data['username']

        if User.objects.exclude(email=email).filter(username=username).exists():
            raise forms.ValidationError(_("Username %s is already in use." % username))
        return username

    def clean_password2(self):
        password1 = self.data.get('password1', None)
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise forms.ValidationError(_("Kata sandi tidak sama."))
        return password2


# edit profile form
class ProfileForm(forms.Form):
    full_name = forms.CharField(label=_("Nama Lengkap"))
    born_place = forms.CharField(label=_("Tempat Lahir"))
    born_date = forms.DateField(
        label=_("Tanggal Lahir"), help_text=_("Format harus: dd-mm-yyyy. Contoh: 26-11-1990"),
        input_formats=['%d-%m-%Y'])
    school_origin = forms.CharField(label=_("Asal Sekolah"))
    graduation_year = forms.CharField(label=_("Tahun Kelulusan"))
    whatsapp = forms.CharField(label=_("Nomor WhatsApp"))
    instagram = forms.CharField(label=_("Akun Instagram"))
    telephone = forms.CharField(label=_("Nomor Ponsel"))


# change sensitive data
class SecureForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(label=_("Kata Sandi"), validators=[validate_password], widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Ulangi Kata Sandi"), widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email', None)

        # Make user email filled
        if email:
            # Validate each account has different email
            if User.objects.filter(email=email).exclude(
                    username=self.request.user.username).exists():
                raise forms.ValidationError(_('Email has been used.'))
        return email

    def clean_password2(self):
        password1 = self.data.get('password1', None)
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise forms.ValidationError(_("Kata sandi tidak sama."))
        return password2
