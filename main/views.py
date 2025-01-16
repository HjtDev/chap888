from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, timedelta
from random import randint
from django.contrib import messages
from random import choice, shuffle
from string import ascii_letters, digits, punctuation
from .models import FAQ


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

def control_panel_view(request):
    if request.method == 'POST':
        try:
            A3 = int(request.POST['A3'])
            A4 = int(request.POST['A4'])
            A5 = int(request.POST['A5'])
            WB = int(request.POST['WB'])
            C50 = int(request.POST['C50'])
            C100 = int(request.POST['C100'])
            ONE_SIDE = int(request.POST['ONE_SIDE'])
            BOTH_SIDES = int(request.POST['BOTH_SIDES'])
            TWO_PAGES_PER_SIDE = int(request.POST['TWO_PAGES_PER_SIDE'])
            COVERED_NO_PUNCH = int(request.POST['COVERED_NO_PUNCH'])
            COVERED_PUNCHED = int(request.POST['COVERED_PUNCHED'])
            NO_BINDING = int(request.POST['NO_BINDING'])

            cache.set('A3', A3, timeout=None)
            cache.set('A4', A4, timeout=None)
            cache.set('A5', A5, timeout=None)
            cache.set('W&B', WB, timeout=None)
            cache.set('C50', C50, timeout=None)
            cache.set('C100', C100, timeout=None)
            cache.set('ONE_SIDE', ONE_SIDE, timeout=None)
            cache.set('BOTH_SIDES', BOTH_SIDES, timeout=None)
            cache.set('TWO_PAGES_PER_SIDE', TWO_PAGES_PER_SIDE, timeout=None)
            cache.set('COVERED_NO_PUNCH', COVERED_NO_PUNCH, timeout=None)
            cache.set('COVERED_PUNCHED', COVERED_PUNCHED, timeout=None)
            cache.set('NO_BINDING', NO_BINDING, timeout=None)

            context = {
                'A3': A3,
                'A4': A4,
                'A5': A5,
                'WB': WB,
                'C50': C50,
                'C100': C100,
                'ONE_SIDE': ONE_SIDE,
                'BOTH_SIDES': BOTH_SIDES,
                'COVERED_NO_PUNCH': COVERED_NO_PUNCH,
                'COVERED_PUNCHED': COVERED_PUNCHED,
                'NO_BINDING': NO_BINDING
            }
            messages.success(request, 'ذخیره شد')
        except (KeyError, ValueError) as e:
            print(e)
            messages.error(request, f'مشکلی در ذخیره اطلاعات پیش آمد لطفا مقادیر را برسی نموده و مجددا تلاش بفرمایید.')
            return redirect('main:control_panel')
    else:
        context = {
            'A3': cache.get('A3'),
            'A4': cache.get('A4'),
            'A5': cache.get('A5'),
            'WB': cache.get('W&B'),
            'C50': cache.get('C50'),
            'C100': cache.get('C100'),
            'ONE_SIDE': cache.get('ONE_SIDE'),
            'BOTH_SIDES': cache.get('BOTH_SIDES'),
            'TWO_PAGES_PER_SIDE': cache.get('TWO_PAGES_PER_SIDE'),
            'COVERED_NO_PUNCH': cache.get('COVERED_NO_PUNCH'),
            'COVERED_PUNCHED': cache.get('COVERED_PUNCHED'),
            'NO_BINDING': cache.get('NO_BINDING')
        }
    return render(request, 'control_panel.html', context)

def price_list(request):
    return JsonResponse({
        'A3': cache.get('A3'),
        'A4': cache.get('A4'),
        'A5': cache.get('A5'),
        'W&B': cache.get('W&B'),
        'C50': cache.get('C50'),
        'C100': cache.get('C100'),
        'ONE_SIDE': cache.get('ONE_SIDE'),
        'BOTH_SIDES': cache.get('BOTH_SIDES'),
        'TWO_PAGES_PER_SIDE': cache.get('TWO_PAGES_PER_SIDE'),
        'COVERED_NO_PUNCH': cache.get('COVERED_NO_PUNCH'),
        'COVERED_PUNCHED': cache.get('COVERED_PUNCHED'),
        'NO_BINDING': cache.get('NO_BINDING')
    })

def generate_password() -> str:
    password = [choice(ascii_letters) + choice(digits) + choice(punctuation) for _ in range(5)]
    shuffle(password)
    return ''.join(password)


def faq_view(request):
    return render(request, 'faq.html', {'faq': FAQ.objects.filter(is_visible=True)})

def terms_of_use_view(request):
    return render(request, 'terms.html')
