from django.contrib import admin
from .models import Order, OrderItem, Transaction, Discount


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
    list_filter = ('user', 'status', 'created_at', 'updated_at')
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
        'description',
        'price',
        'created_at'
    )
    list_filter = (
        'created_at',
        'reason',
        'status'
    )
    search_fields = ('id',)
    ordering = ('created_at',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('token', 'value', 'expire_at')
    list_filter = ('expire_at',)
    search_fields = ('token', 'value')
    readonly_fields = ('used_by',)
