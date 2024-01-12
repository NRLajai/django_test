from django.contrib import admin
from .models import *

@admin.register(LikedItem)
class LikedItemAdmin(admin.ModelAdmin):
    pass

