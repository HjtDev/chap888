from django.contrib import admin
from .models import Order, OrderItem, Transaction, Discount
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin
from account.models import User
from jdatetime import datetime


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    verbose_name = 'آیتم'
    verbose_name_plural = 'آیتم ها'
    readonly_fields = ('document',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'user',
        'phone',
        'province',
        'city',
        'created_at',
        'status'
    )
    list_filter = ('user', 'status', ('created_at', JDateFieldListFilter), ('updated_at', JDateFieldListFilter))
    search_fields = (
        'first_name',
        'last_name',
        'phone',
        'province',
        'city',
        'email',
        'address',
        'postal_code',
        'notes'
    )
    list_editable = ('status',)
    ordering = ('-created_at',)
    inlines = (OrderItemInline,)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'reason',
        'status',
        'price',
        'created_at'
    )
    list_filter = (
        ('created_at', JDateFieldListFilter),
        'reason',
        'status'
    )
    list_editable = ('reason', 'status')
    search_fields = ('id', 'description')
    ordering = ('created_at',)


@admin.action(description='ارسال کد تخفیف برای کاربران')
def send_discount_to_users(modeladmin, request, queryset):
    for discount in queryset.all():
        for user in User.objects.all():
            if discount.validate(user.phone):
                print(f'SMS Notification - Discount for {user.phone} | Code: {discount.token}')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('token', 'value', 'expire_at')
    list_filter = ('expire_at', JDateFieldListFilter),
    search_fields = ('token', 'value')
    readonly_fields = ('used_by',)
    actions = [send_discount_to_users]
