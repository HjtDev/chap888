from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders',
                             verbose_name='کاربر')
    first_name = models.CharField(max_length=255, verbose_name='نام')
    last_name = models.CharField(max_length=255, verbose_name='نام خانوادگی')
    email = models.EmailField(max_length=255, verbose_name='ایمیل', blank=True, null=True)
    phone = models.CharField(max_length=11, verbose_name='شماره تلفن')
    province = models.CharField(max_length=255, verbose_name='استان', blank=True, null=True)
    city = models.CharField(max_length=255, verbose_name='شهرستان', blank=True, null=True)
    address = models.CharField(max_length=300, verbose_name='آدرس', blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی', blank=True, null=True)
    notes = models.TextField(max_length=500, verbose_name='یادداشت های سفارش', blank=True, null=True)

    order_id = models.CharField(verbose_name='کد سفارش', max_length=10, default='')
    postal_id = models.CharField(verbose_name='کد رهگیری پست', max_length=30, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین تغییر')

    class OrderStatus(models.TextChoices):
        SUBMITTED = 'ثبت شده', _('ثبت شده')
        CONFIRMED = 'پرداخت شده', _('پرداخت شده')
        PREPARING = 'آماده سازی سفارش', _('آماده سازی سفارش')
        DELIVERING = 'در حال ارسال', _('در حال ارسال')
        DONE = 'تکمیل شد', _('تکمیل شد')
        ABORTED = 'لغو شد', _('لغو شد')

    status = models.CharField(max_length=21, choices=OrderStatus.choices, default=OrderStatus.SUBMITTED,
                              verbose_name='وضعیت')

    def __str__(self):
        return f'Order-{self.order_id}: {self.first_name} {self.last_name}'

    def get_total_price(self, post_price, discount):
        return max(0, sum(item.get_item_cost() for item in self.items.all()) + post_price - discount)

    get_total_price.short_description = 'هزینه نهایی'

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    price = models.PositiveIntegerField(default=0, verbose_name='قیمت')
    quantity = models.PositiveIntegerField(default=1, verbose_name='سری')

    class SizeChoices(models.TextChoices):
        A3 = ('A3', 'A3')
        A4 = ('A4', 'A4')
        A5 = ('A5', 'A5')

    class ColorChoices(models.TextChoices):
        WB = ('W&B', _('سیاه سفید'))
        C50 = ('C50', _('رنگی 50 درصد'))
        C100 = ('C100', _('رنگی 100 درصد'))

    class TypeChoices(models.TextChoices):
        ONE_SIDE = ('ONE_SIDE', _('یک رو'))
        BOTH_SIDES = ('BOTH_SIDES', _('دو رو'))

    class ExtraChoices(models.TextChoices):
        NO_BINDING = ('NO_BINDING', _('بدون صحافی'))
        COVERED_NO_PUNCH = ('COVERED_NO_PUNCH', _('کاور شده بدون پانچ'))
        COVERED_PUNCHED = ('COVERED_PUNCHED', _('کاور شده با پانچ'))

    size = models.CharField(max_length=2, choices=SizeChoices.choices, verbose_name='اندازه')
    color = models.CharField(max_length=21, choices=ColorChoices.choices, verbose_name='رنگ')
    print_type = models.CharField(max_length=21, choices=TypeChoices.choices, verbose_name='نوع چاپ')
    extra = models.CharField(max_length=21, choices=ExtraChoices.choices, verbose_name='نوع صحافی')

    def get_item_cost(self):
        return (cache.get(self.size) + cache.get(self.color) + cache.get(self.extra)) * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_item_cost()
        return super().save(*args, **kwargs)

    get_item_cost.short_description = 'قیمت'

class Transaction(models.Model):
    class ReasonChoice(models.TextChoices):
        ORDER = 'برای سفارش', _('برای سفارش')
        REFUND = 'بازگشت وجه', _('بازگشت وجه')

    class TransactionStatusChoice(models.TextChoices):
        PAID = 'پرداخت موفق', _('پرداخت موفق')
        FAILED = 'پرداخت ناموفق', _('پرداخت ناموفق')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='transactions', verbose_name='کاربر',
                             blank=True, null=True)
    reason = models.CharField(verbose_name='علت تراکنش', choices=ReasonChoice.choices, max_length=21)
    status = models.CharField(verbose_name='وضعیت تراکنش', choices=TransactionStatusChoice.choices, max_length=21)
    description = models.TextField(verbose_name='توضیحات نراکنش')
    price = models.PositiveIntegerField(verbose_name='هزینه', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'
        ordering = ('created_at',)

    def __str__(self):
        return f'تراکنش شماره {self.id}'
