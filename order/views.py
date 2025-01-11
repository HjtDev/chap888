from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from cart.cart import Cart
from .forms import OrderForm
from uuid import uuid4
from .models import OrderItem, Order
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
                OrderItem.objects.create(order=order, quantity=int(item['quantity']), size=options['page_size'],
                                         color=options['print_color'], print_type=options['print_type'],
                                         extra=options['extra_options'])
            cart.clear()
            request.session['order'] = order.pk
            specials = []
            if 'shipment' in request.POST:
                specials.append('post_wanted')
            if 'ship-special-address' in request.POST:
                specials.append('free_post')
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
        specials = cache.get(f'order_specials:{order_pk}')
        cache.delete(f'order_specials:{order_pk}')
        post_price = 25000 if 'post_wanted' in specials and 'free_post' not in specials else 0
        total = order.get_total_price(post_price, 1100)
        return HttpResponse(f'Payment: {total} Toman')
    except Order.DoesNotExist:
        pass
