from django.shortcuts import render, reverse, redirect
from django.http import JsonResponse
from datetime import datetime, timedelta
from random import randint
from django.contrib import messages
from django.core.cache import cache
from random import choice, shuffle
from string import ascii_letters, digits, punctuation
from .models import FAQ
import threading, json, os
from django.conf import settings


SETTINGS_FILE = os.path.join(settings.BASE_DIR, 'prices.json')
lock = threading.Lock()

def load_prices():
    """Load prices from the JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_prices(prices):
    """Save prices to the JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(prices, f)


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
    prices = load_prices()

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

            with lock:
                prices.update({
                    'A3': A3,
                    'A4': A4,
                    'A5': A5,
                    'WB': WB,
                    'C50': C50,
                    'C100': C100,
                    'ONE_SIDE': ONE_SIDE,
                    'BOTH_SIDES': BOTH_SIDES,
                    'TWO_PAGES_PER_SIDE': TWO_PAGES_PER_SIDE,
                    'COVERED_NO_PUNCH': COVERED_NO_PUNCH,
                    'COVERED_PUNCHED': COVERED_PUNCHED,
                    'NO_BINDING': NO_BINDING
                })
                context = prices
                save_prices(prices)

            messages.success(request, 'ذخیره شد.')
        except (KeyError, ValueError) as e:
            print(e)
            messages.error(request, f'مشکلی در ذخیره اطلاعات پیش آمد لطفا مقادیر را برسی نموده و مجددا تلاش بفرمایید.')
            return redirect('main:control_panel')
    else:
        context = {
            'A3': prices.get('A3'),
            'A4': prices.get('A4'),
            'A5': prices.get('A5'),
            'WB': prices.get('WB'),
            'C50': prices.get('C50'),
            'C100': prices.get('C100'),
            'ONE_SIDE': prices.get('ONE_SIDE'),
            'BOTH_SIDES': prices.get('BOTH_SIDES'),
            'TWO_PAGES_PER_SIDE': prices.get('TWO_PAGES_PER_SIDE'),
            'COVERED_NO_PUNCH': prices.get('COVERED_NO_PUNCH'),
            'COVERED_PUNCHED': prices.get('COVERED_PUNCHED'),
            'NO_BINDING': prices.get('NO_BINDING')
        }
    return render(request, 'control_panel.html', context)


def price_list(request):
    prices = load_prices()
    return JsonResponse({
        'A3': prices.get('A3'),
        'A4': prices.get('A4'),
        'A5': prices.get('A5'),
        'W&B': prices.get('W&B'),
        'C50': prices.get('C50'),
        'C100': prices.get('C100'),
        'ONE_SIDE': prices.get('ONE_SIDE'),
        'BOTH_SIDES': prices.get('BOTH_SIDES'),
        'TWO_PAGES_PER_SIDE': prices.get('TWO_PAGES_PER_SIDE'),
        'COVERED_NO_PUNCH': prices.get('COVERED_NO_PUNCH'),
        'COVERED_PUNCHED': prices.get('COVERED_PUNCHED'),
        'NO_BINDING': prices.get('NO_BINDING')
    })

def generate_password() -> str:
    password = [choice(ascii_letters) + choice(digits) + choice(punctuation) for _ in range(5)]
    shuffle(password)
    return ''.join(password)


def faq_view(request):
    return render(request, 'faq.html', {'faq': FAQ.objects.filter(is_visible=True)})

def terms_of_use_view(request):
    return render(request, 'terms.html')
