from django.shortcuts import render
from django.core.cache import cache

from cart.cart import Cart


def checkout_view(request):
    cart = Cart(request, converted=False)
    items = []
    total = 0
    for item in cart:
        items.append((str(item['document']), item['quantity']))
        options = item['options']
        total += (cache.get(options['page_size']) + cache.get(options['print_color']) + cache.get(
            options['extra_options'])) * int(item['quantity'])
    return render(request, 'checkout.html', {'items': items, 'total': total})
