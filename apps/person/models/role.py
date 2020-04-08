import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from utils.generals import get_model
from apps.person.utils.constant import SELECT_ROLES, REGISTERED

try:
    _REGISTERED = REGISTERED
except NameError:
    _REGISTERED = None

try:
    _SELECT_ROLES = SELECT_ROLES
except NameError:
    _SELECT_ROLES = list()


class AbstractRole(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='roles')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    role = models.CharField(choices=_SELECT_ROLES, blank=False,
                            null=False, default=_REGISTERED, max_length=255)

    class Meta:
        abstract = True
        app_label = 'person'
        ordering = ['-user__date_joined']
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return self.role

    def clean(self):
        if self.role not in dict(SELECT_ROLES):
            raise ValidationError(_("Role %s not available." % (self.role)))


class AbstractRoleCapabilities(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    role = models.CharField(
        choices=SELECT_ROLES, blank=False, null=False, max_length=255)
    permissions = models.ManyToManyField(
        Permission,
        related_name='role_capabilities')

    class Meta:
        abstract = True
        app_label = 'person'
        verbose_name = _("Role Capability")
        verbose_name_plural = _("Role Capabilities")
        constraints = [
            models.UniqueConstraint(fields=['role'], name='unique_role')
        ]

    def __str__(self):
        return self.role
