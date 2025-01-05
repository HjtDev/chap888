from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.core.cache import cache
from datetime import datetime, timedelta
from random import randint
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            cache.set(f'register:{user.phone}', user, timeout=130)
            expire = datetime.now() + timedelta(minutes=2)
            request.session['auth'] = {'phone': user.phone, 'token': str(randint(100000, 999999)),
                                       'time': expire.strftime('%Y-%m-%dT%H:%M:%S'), 'prev': 'account:register'}
            request.session.modified = True
            return redirect('account:verify')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        return render(request, 'register.html')


def verify_view(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    auth = request.session.get('auth')
    if not auth:
        return redirect('main:index')
    if request.method == 'POST':
        if datetime.now() > datetime.strptime(auth['time'], '%Y-%m-%dT%H:%M:%S'):
            messages.error(request, 'کد تایید منقضی شده است لطفا دوباره تلاش کنید.')
            prev_page = auth['prev']
            del auth
            return redirect(prev_page)
        token = request.POST.get('token')
        if token != auth['token']:
            messages.error(request, 'کد تایید اشتباه است.')
            return render(request, 'verify.html')
        elif token == auth['token']:
            phone = auth['phone']
            user: User = cache.get(f'register:{phone}')
            if user:
                user.save()
                del request.session['auth']
                target_page: str | None = request.session.get('next', None)
                session = request.session
                login(request, user)
                request.session = session
                request.session.modified = True
                if target_page is not None:
                    del request.session['next']
                    return redirect(target_page)
                return redirect('main:index')

            else:
                messages.error(request, 'در فرایند ثبت نام مشکلی پیش آمد لطفا مجددا تلاش کنید و در صورت حل نشدن مشکل با پشتیبانی سایت تماس بگیرید.')
                prev_page = auth['prev']
                del auth
                return redirect(prev_page)
    else:
        print(auth.get('token'))
        return render(request, 'verify.html')
