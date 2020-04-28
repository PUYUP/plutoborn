from django.contrib import admin

# Register your models here.
from utils.generals import get_model

CMSBanner = get_model('cms', 'CMSBanner')
CMSVideo = get_model('cms', 'CMSVideo')

admin.site.register(CMSBanner)
admin.site.register(CMSVideo)
