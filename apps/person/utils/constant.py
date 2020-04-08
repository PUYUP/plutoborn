from django.utils.translation import ugettext_lazy as _

ADMIN = 'admin'
STAFF = 'staff'
REGISTERED = 'registered'
SELECT_ROLES = (
    (ADMIN, _("Admin")),
    (STAFF, _("Staff")),
    (REGISTERED, _("Registered")),
)


EMAIL_VALIDATION = 'email_validation'
CHANGE_EMAIL_VALIDATION = 'change_email_validation'
TELEPHONE_VALIDATION = 'telephone_validation'
CHANGE_TELEPHONE_VALIDATION = 'change_telephone_validation'
REGISTER_VALIDATION = 'register_validation'
OTP_IDENTIFIER = (
    (EMAIL_VALIDATION, _("Email Validation")),
    (CHANGE_EMAIL_VALIDATION, _("Change Email Validation")),
    (TELEPHONE_VALIDATION, _("Telephone Validation")),
    (CHANGE_TELEPHONE_VALIDATION, _("Change Telephone Validation")),
    (REGISTER_VALIDATION, _("Register Validation")),
)
