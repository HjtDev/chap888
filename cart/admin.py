from django.contrib import admin
from .models import Documents
from django.utils.html import format_html


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_page_count')
    list_display_links = ( '__str__', 'get_page_count')
