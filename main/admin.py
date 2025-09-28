from django.contrib import admin
from .models import FAQ, Comment
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('question', 'answer')
    list_editable = ('is_visible',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'commented_at', 'is_visible')
    list_filter = (('commented_at', JDateFieldListFilter), 'is_visible')
    search_fields = ('name', 'text')
    list_editable = ('is_visible',)

