from django.contrib import admin

from utils.generals import get_model

Points = get_model('mypoints', 'Points')

# Register your models here.
admin.site.register(Points)
