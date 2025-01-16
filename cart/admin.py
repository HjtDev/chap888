from django.contrib import admin
from .models import Documents
from django.utils.html import format_html


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_image', '__str__', 'get_page_count')
    list_display_links = ('thumbnail_image', '__str__', 'get_page_count')

    def thumbnail_image(self, obj):
        if obj.thumbnail:  # Check if the thumbnail exists
            return format_html('<img src="{}" style="max-width: 60px; max-height: 70px;" />', obj.thumbnail.url)
        return "No Image"

    thumbnail_image.short_description = 'پیش نمایش'

