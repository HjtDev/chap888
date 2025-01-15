from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from cart.cart import Cart
from .forms import OrderForm
from uuid import uuid4
from .models import OrderItem, Order, Discount
from account.models import User
from main.views import sms_authentication, generate_password


def checkout_view(request):
    cart = Cart(request, converted=False)
    items = []
    total = 0
    for item in cart:
        items.append((str(item['document']), item['quantity']))
        options = item['options']
        total += (cache.get(options['page_size']) + cache.get(options['print_color']) + cache.get(
            options['print_type']) + cache.get(options['extra_options'])) * int(item['quantity'])
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
        total = 0
        if discount_token:
            discount = Discount.objects.get(token=discount_token[0])
            if discount.validate(order.phone):
                discount.used_by.add(order.user)
                discount.save()
                total = order.get_total_price(post_price, discount)
        else:
            total = order.get_total_price(post_price)
        return HttpResponse(f'Payment: {total} Toman')
    except Order.DoesNotExist:
        print('Order does not exist')
    except Discount.DoesNotExist:
        print('Discount does not exist')


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
