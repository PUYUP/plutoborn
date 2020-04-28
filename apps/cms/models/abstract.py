import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.cms.utils import LINK_TARGET, SELF_WINDOW


class AbstractCMSBanner(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    label = models.CharField(max_length=255)
    sort = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    link_to = models.CharField(max_length=500, blank=True)
    link_target = models.CharField(choices=LINK_TARGET, default=SELF_WINDOW,
                                   blank=True, max_length=255)
    image = models.ImageField(upload_to='images/banner', max_length=500, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")

    def __str__(self):
        return self.label


class AbstractCMSVideo(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    label = models.CharField(max_length=255)
    sort = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    video_url = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")

    def __str__(self):
        return self.label
