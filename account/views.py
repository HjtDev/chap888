from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from json import loads
from .forms import RegisterForm
from django.core.cache import cache
from datetime import datetime, timedelta
from random import randint
from .models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from main.views import sms_authentication


def login_user(request, user):
    session = request.session
    login(request, user)
    request.session = session
    request.session.modified = True


def logout_view(request):
    logout(request)
    return redirect('account:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            return sms_authentication(request, user.phone, user, 'account:register')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        return render(request, 'register.html')


def login_view(request, phone=None):
    if request.user.is_authenticated:
        return redirect('main:index')
    if phone:
        try:
            user = User.objects.get(phone=phone)
            return sms_authentication(request, phone, user, 'account:login')
        except User.DoesNotExist:
            messages.error(request, 'کاربری با این شماره تلفن یافت نشد.')
            return render(request, 'login.html')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('phone'), password=request.POST.get('password'))
        if not user:
            messages.error(request, 'شماره تلفن یا گذرواژه صحیح نمی باشد.')
            return render(request, 'login.html', {'phone': request.POST.get('phone')})
        else:
            target_page: str | None = request.session.get('next', None)
            login_user(request, user)
            if target_page is not None:
                del request.session['next']
                return redirect(target_page)
            return redirect('main:index')
    else:
        return render(request, 'login.html')


def verify_view(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    auth = request.session.get('auth', None)
    if not auth:
        return redirect('account:login')
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
            if request.session.get('reset'):
                return redirect('account:reset_complete', request.session['reset'])
            user: User = cache.get(f'authenticate:{phone}')
            if user:
                user.save()
                del request.session['auth']
                target_page: str | None = request.session.get('next', None)
                login_user(request, user)
                if target_page is not None:
                    del request.session['next']
                    return redirect(target_page)
                return redirect('main:index')

            else:
                messages.error(request,
                               'در فرایند ثبت نام مشکلی پیش آمد لطفا مجددا تلاش کنید و در صورت حل نشدن مشکل با پشتیبانی سایت تماس بگیرید.')
                prev_page = auth['prev']
                del auth
                return redirect(prev_page)
    else:
        return render(request, 'verify.html')


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        try:
            phone = loads(request.body).get('phone')
            user = User.objects.get(phone=phone)
            if user is not None:
                request.session['reset'] = phone
                return sms_authentication(request, phone, user, 'account:login', json_response=True)
        except User.DoesNotExist:
            messages.error(request, 'کاربری با این شماره تلفن وجود ندارد.')
            return JsonResponse({'redirect': reverse('account:login')})


def reset_password_complete_view(request, phone):
    if request.user.is_authenticated:
        return redirect('main:index')
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'گذرواژه ها با یکدیگر تطابق ندارند.')
            return render(request, 'reset_password.html')
        try:
            password_validation.validate_password(password1)
            user = User.objects.get(phone=phone)
            if request.session.get('reset', None) == phone:
                user.set_password(password1)
                user.save()
                del request.session['reset']
                del request.session['auth']
                request.session.modified = True
                return redirect('account:login')
        except ValidationError as e:
            messages.error(request, e.messages)
            return render(request, 'reset_password.html')

    else:
        token = request.session.get('reset')
        if token and token == phone:
            return render(request, 'reset_password.html')
        messages.warning(request, 'دسترسی محدود شد لطفا مجددا تلاش کنید.')
        return redirect('account:login')
