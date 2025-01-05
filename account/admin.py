from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeFormNew
from django.contrib.auth.models import Group

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ['phone']

    add_form = UserCreationForm
    form = UserChangeFormNew
    model = User

    search_fields = [
        'phone',
        'first_name',
        'last_name',
        'email'
    ]

    list_display = [
        'phone',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
    ]

    fieldsets = (
        ('اصلی', {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی ها', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('تاریخ ها', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('اصلی', {'fields': ('phone', 'password1', 'password2')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ ها', {'fields': ('last_login', 'date_joined')}),
    )
