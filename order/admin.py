from django.contrib import admin
from .models import Order, OrderItem, Transaction


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    verbose_name = 'آیتم'
    verbose_name_plural = 'آیتم ها'


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
        'user',
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
