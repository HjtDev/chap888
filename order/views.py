from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from cart.cart import Cart
from .forms import OrderForm
from uuid import uuid4
from .models import OrderItem, Order, Discount, Transaction
from account.models import User
from main.views import sms_authentication, generate_password
from main.views import load_prices


def checkout_view(request):
    cart = Cart(request, converted=False)
    items = []
    total = 0
    prices = load_prices()
    for item in cart:
        items.append((str(item['document']), item['quantity']))
        options = item['options']
        pages = item['document'].get_page_count()
        if options['print_type'] != 'ONE_SIDE' and pages % 2 != 0:
            pages += 1
        if options['print_type'] == 'BOTH_SIDES':
            pages = max(1, pages // 2)
        elif options['print_type'] == 'TWO_PAGES_PER_SIDE':
            pages = max(1, pages // 4)
        total += (prices.get(options['page_size']) + prices.get(options['print_color']) + prices.get(
            options['print_type']) + prices.get(options['extra_options'])) * pages * int(item['quantity'])
    if not items:
        messages.error(request, 'سبد خرید شما خالی است')
        return redirect('cart:cart')
    return render(request, 'checkout.html', {'items': items, 'total': total})


def submit_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        auth_required = not request.user.is_authenticated
        if form.is_valid():
            order = form.save(commit=False)
            order.order_id = str(uuid4())[:10]
            if not auth_required:
                order.user = request.user
            order.save()
            cart = Cart(request, converted=False)
            for item in cart:
                options = item['options']
                OrderItem.objects.create(order=order, document=item['document'], quantity=int(item['quantity']), size=options['page_size'],
                                         color=options['print_color'], print_type=options['print_type'],
                                         extra=options['extra_options'])
            cart.clear()
            request.session['order'] = order.pk
            specials = []
            if 'shipment' in request.POST:
                specials.append('post_wanted')
            if 'ship-special-address' in request.POST:
                specials.append('free_post')
            token = request.POST.get('discount_token')
            if token:
                specials.append(f'discount:{token}')
            cache.set(f'order_specials:{order.pk}', specials)
            if auth_required:
                try:
                    user = User.objects.get(phone=order.phone)
                    request.session['next'] = 'order:complete_order'
                    return sms_authentication(request, user.phone, user, 'cart:cart')
                except User.DoesNotExist:
                    user = User(
                        phone=order.phone,
                        first_name=order.first_name,
                        last_name=order.last_name,
                        email=order.email,
                    )
                    user.set_password(generate_password())
                    request.session['next'] = 'order:complete_order'
                    return sms_authentication(request, user.phone, user, 'cart:cart')
            else:
                return redirect('order:complete_order')
        else:
            return render(request, 'checkout.html', {'form': form})


def complete_order_view(request):
    if not request.user.is_authenticated or not request.session.get('order'):
        return redirect('cart:cart')
    try:
        order_pk = request.session['order']
        order = Order.objects.get(pk=order_pk)
        if not order.user:
            order.user = request.user
            order.save()
        specials = cache.get(f'order_specials:{order_pk}')
        cache.delete(f'order_specials:{order_pk}')
        post_price = 25000 if 'post_wanted' in specials and 'free_post' not in specials else 0
        discount_token = [special.split(':')[-1] for special in specials if 'discount' in special]
        base = 0
        total = 0
        discount = None
        if discount_token:
            discount = Discount.objects.get(token=discount_token[0])
            if discount.validate(order.phone):
                discount.used_by.add(order.user)
                discount.save()
                base, total = order.get_total_price(post_price, discount)
        else:
            base, total = order.get_total_price(post_price)
        transaction = Transaction(
            user = order.user,
            order = order,
            reason = Transaction.ReasonChoice.ORDER,
            status = Transaction.TransactionStatusChoice.PENDING,
            price = total,
            description = ''
        )
        transaction_text = []
        if discount_token:
            transaction_text.append(f'کد تخفیف: {discount_token[0]}')
            transaction_text.append(f'مقدار تخفیف: {discount.value}')
        transaction_text.append(f'هزینه پست: {post_price}')
        transaction_text.append(f'قیمت پایه: {base}')
        transaction_text.append(f'قیمت نهایی: {total}')
        for item in order.items.all():
            transaction_text.append(str(item))
        transaction.description = '\n'.join(transaction_text)
        transaction.save()
        messages.info(request, 'مشتری گرامی در صورت تایید شدن سفارش شما کد سفارش برای شما ارسال خواهد شد. پس از دریافت کد سفارش می توانید وضعیت سفارش خود را از صفحه "وضعیت سفارش" برسی کنید.')
        if total > 0:
            messages.info(request, f'پس از دریافت کد سفارش خود مبلغ {total} تومان را به شماره کارت 6037998209302941 به نام محمد تقی جمشیدی واریز کنید.')
            messages.info(request, 'پس از واریز از طریق چت پشتیبانی یا با تماس با شماره 09133382078 اطلاعات فیش واریز و کد سفارش خود را ارسال کنید تا در اولین فرصت سفارش شما پیگیری شود.')
        return redirect('order:result')
    except Order.DoesNotExist:
        messages.warning(request, 'شما سفارش خود را لغو کردید.')
    except Discount.DoesNotExist:
        messages.warning(request, 'شما سفارش خود را لغو کردید.')
    return redirect('cart:cart')


def check_discount(request):
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone') if not request.user.is_authenticated else request.user.phone
            discount = Discount.objects.get(token=request.POST.get('token'))
            price = int(request.POST.get('price'))
            if phone and len(phone) == 11 and phone.isdigit() and phone.startswith('09'):
                if discount.validate(phone):
                    return JsonResponse({'ok': True, 'discount': discount.calculate(price)})
                else:
                    return JsonResponse({'ok': False, 'error': 'کد تخفیف منقضی شده است.'})
            else:
                return JsonResponse({'ok': False, 'error': 'شماره تلفن معتبر نیست.'})
        except Discount.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'کد تخفیف معتبر نیست.'})
        except ValueError:
            return JsonResponse({'ok': False, 'error': 'قیمت باید یک عدد باشد.'})
    else:
        return JsonResponse({'ok': False, 'error': 'Invalid Method'})


def status_view(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('order-code')
            order = Order.objects.get(order_id=order_id)
            messages.info(request, f'سفارش شما در وضعیت "{order.status}" قرار دارد.')
        except Order.DoesNotExist:
            messages.error(request, 'کد سفارش اشتباه است.')
    return render(request, 'status.html')


def result_view(request):
    return render(request, 'result.html')
