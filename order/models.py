from django.core.exceptions import ValidationError
from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from cart.models import Documents
from django.utils import timezone
from django_jalali.db import models as jmodels
from main.views import load_prices


class Order(models.Model):
    objects = jmodels.jManager()

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
    postal_id = models.CharField(verbose_name='کد رهگیری پست', blank=True, null=True)

    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = jmodels.jDateTimeField(auto_now=True, verbose_name='آخرین تغییر')

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

    def get_total_price(self, post_price, discount: 'Discount' = None):
        price = sum(item.price for item in self.items.all())
        return (price + post_price - discount.calculate(price)) if discount else price + post_price

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
    document = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='order_items', verbose_name='فایل')
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
        TWO_PAGES_PER_SIDE = ('TWO_PAGES_PER_SIDE', _('هر دو صفحه یک رو'))

    class ExtraChoices(models.TextChoices):
        NO_BINDING = ('NO_BINDING', _('بدون صحافی'))
        COVERED_NO_PUNCH = ('COVERED_NO_PUNCH', _('کاور شده بدون پانچ'))
        COVERED_PUNCHED = ('COVERED_PUNCHED', _('کاور شده با پانچ'))

    size = models.CharField(max_length=2, choices=SizeChoices.choices, verbose_name='اندازه')
    color = models.CharField(max_length=21, choices=ColorChoices.choices, verbose_name='رنگ')
    print_type = models.CharField(max_length=21, choices=TypeChoices.choices, verbose_name='نوع چاپ')
    extra = models.CharField(max_length=21, choices=ExtraChoices.choices, verbose_name='نوع صحافی')

    def get_item_cost(self):
        prices = load_prices()
        pages = self.document.get_page_count()
        if self.print_type != self.TypeChoices.ONE_SIDE and pages % 2 != 0:
            pages += 1

        if self.print_type == self.TypeChoices.BOTH_SIDES:
            pages = max(1, pages // 2)
        elif self.print_type == self.TypeChoices.TWO_PAGES_PER_SIDE:
            pages = max(1, pages // 4)

        return (prices.get(self.size) + prices.get(self.color) + prices.get(self.print_type) + prices.get(
            self.extra)) * pages * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_item_cost()
        return super().save(*args, **kwargs)

    get_item_cost.short_description = 'قیمت'


class Transaction(models.Model):
    objects = jmodels.jManager()

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
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'
        ordering = ('created_at',)

    def __str__(self):
        return f'تراکنش شماره {self.id}'


def discount_value_validator(value: str):
    print((0 < int(value.replace('%', '')) <= 100))
    if '%' in value:
        if not (0 < int(value.replace('%', '')) <= 100):
            raise ValidationError('مقدار تخفیف به درصد باید حداقل 1 و حداکثر 100 باشد.')
    else:
        if not value.isdigit() or not (0 < int(value) <= 1_000_000):
            raise ValidationError('مقدار تخفیف به تومان باید فقط یک عدد بین 1 تا 1،000،000 باشد.')


class Discount(models.Model):
    objects = jmodels.jManager()

    token = models.CharField(max_length=20, unique=True, verbose_name='کد تخفیف')
    value = models.CharField(max_length=7, verbose_name='مقدار تخفیف', help_text='تخفیف به تومان یا درصد',
                             validators=[discount_value_validator])
    expire_at = jmodels.jDateTimeField(verbose_name='تاریخ انقضا')

    used_by = models.ManyToManyField(User, related_name='used_discounts', verbose_name='کاربر')

    def __str__(self):
        return f'{self.id} -- {self.token} -- {self.value}'

    def validate(self, phone):
        return not (timezone.now() > self.expire_at or self.used_by.filter(phone=phone).exists())

    def calculate(self, price):
        if '%' in self.value:
            total = int(price * (1 - float(self.value.replace('%', '')) / 100))
        else:
            total = max(0, price - int(self.value))
        return price - total

    class Meta:
        verbose_name = 'تخفیف'
        verbose_name_plural = 'تخفیف ها'
        ordering = ['-expire_at']
        indexes = [
            models.Index(fields=['-expire_at']),
        ]




