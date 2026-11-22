from django.contrib import admin

from .models import Picture


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created")
    list_filter = ("owner",)
    search_fields = ("title", "description")
