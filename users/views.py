from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .forms import UserRegisterForm, UserLoginForm
from .models import User


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_welcome_email(user)
            login(request, user)
            messages.success(request, _('регистрация успешна,добро пожаловать'))
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def send_welcome_email(user):
    subject = _('Добро пожаловать')
    message = _(
        f'привет, {user.email}!\n\n'
        f'спасибо за регистрацию.\n'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('имя фамилия')
            password = form.cleaned_data.get('пароль')
            user = authenticate(request, email=email, password=password)

    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, _('Successfully logged out!'))


@login_required
def profile_view(request):

    return render(request, 'users/profile.html', {'user': request.user})