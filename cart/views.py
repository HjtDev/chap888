from django.shortcuts import render

# Create your views here.
def test_view(request):
    cart = Cart(request)
    cart.add(Documents.objects.first().id, 1, 'A4', 'W&B', 'ONE_SIDE', 'NO_BINDING')
    cart.add(Documents.objects.last().id, 2, 'A3', 'C50', 'BOTH_SIDES', 'COVERED_PUNCHED')
    items = [item for item in cart]

    return JsonResponse({'ok': True})
