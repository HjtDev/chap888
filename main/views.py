from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, timedelta
from random import randint
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def sms_authentication(request, phone, user, previous_page='main:index', json_response: bool = False):
    def response():
        if json_response:
            return JsonResponse({'redirect': reverse('account:verify')})
        else:
            return redirect('account:verify')
    if not cache.get(f'authenticate:{phone}', None):
        cache.set(f'authenticate:{phone}', user, timeout=120)
        expire = datetime.now() + timedelta(minutes=2)
        request.session['auth'] = {'phone': phone, 'token': str(randint(100000, 999999)),
                                   'time': expire.strftime('%Y-%m-%dT%H:%M:%S'), 'prev': previous_page}
        request.session.modified = True
        print('SMS Verification:', request.session['auth']['token'])
        messages.success(request, f'کد تایید به {request.session["auth"]["phone"]} پیامک شد.')
        return response()
    messages.info(request, f'کد تایید اخیرا برای شما ارسال شده است.')
    messages.info(request, f'جهت ارسال مجدد پیامک 2 دقیقه صبر کنید.')
    return response()

def price_list(request):
    return JsonResponse({
        'A3': cache.get('A3'),
        'A4': cache.get('A4'),
        'A5': cache.get('A5'),
        'W&B': cache.get('W&B'),
        'C50': cache.get('C50'),
        'C100': cache.get('C100'),
        'COVERED_NO_PUNCH': cache.get('COVERED_NO_PUNCH'),
        'COVERED_PUNCHED': cache.get('COVERED_PUNCHED'),
        'NO_BINDING': cache.get('NO_BINDING')
    })

