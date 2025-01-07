from django.http import JsonResponse
from django.shortcuts import render
from .cart import Cart
from .models import Documents


def cart_view(request):
    return render(request, 'cart.html', {'cart': Cart(request)})

def test_view(request):
    cart = Cart(request)
    cart.add(Documents.objects.first().id, 1, 'A4', 'W&B', 'ONE_SIDE', 'NO_BINDING')
    cart.add(Documents.objects.last().id, 2, 'A3', 'C50', 'BOTH_SIDES', 'COVERED_PUNCHED')
    items = [item for item in cart]

    return JsonResponse({'ok': True})

def delete_view(request):
    if request.method == 'POST':
        try:
            document = Documents.objects.get(id=request.POST.get('document_id'))
            cart = Cart(request)
            if cart.remove(document.id):
                document.delete()
            return JsonResponse({'ok': True})
        except Documents.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'فایلی یافت نشد.'})
    else:
        return JsonResponse({'ok': False, 'error': 'Method not supported'})
