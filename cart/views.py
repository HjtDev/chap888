from django.http import JsonResponse
from django.shortcuts import render
from .cart import Cart
from .models import Documents
from json import loads


def cart_view(request):
    return render(request, 'cart.html')


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


def upload_view(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file:
            doc = Documents.objects.create(pdf=pdf_file)
            cart = Cart(request)
            cart.add(doc.id, 1, 'A4', 'W&B', 'BOTH_SIDES', 'NO_BINDING')
            return JsonResponse(
                {'ok': True, 'thumbnail': doc.thumbnail.url, 'filename': str(doc), 'filepath': doc.pdf.url,
                 'id': doc.id,
                 'pages': doc.get_page_count()})
        return JsonResponse({'ok': False, 'error': 'فایل آپلود نشد لطفا اینترنت خود را برسی کرده و مجددا تلاش کنید'})
    return JsonResponse({'ok': False, 'error': 'مشکلی در آپلود فایل به وجود امد لطفا مجددا تلاش کنید.'})


def save_view(request):
    if request.method == 'POST':
        data = loads(request.body)
        cart = Cart(request)
        for doc_id, options in data.items():
            result = cart.add(doc_id, **options)
            if isinstance(result, str):
                return JsonResponse({'ok': False, 'error': result})
        return JsonResponse({'ok': True})
