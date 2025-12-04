from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import *

def home(request):
    return render(request, 'main/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    """Обработка входа пользователей в систему"""
    if request.method == 'POST':
        # Получение данных из формы
        username = request.POST['username']
        password = request.POST['password']
        # Проверка подлинности пользователя
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Успешная аутентификация - вход в систему
            login(request, user)
            return redirect('profile')
        else:
            # Ошибка аутентификации
            error = "Неверное имя пользователя или пароль"
            return render(request, 'main/login.html', {'error': error})
    
    return render(request, 'main/login.html')

def logout_view(request):
    """Выход пользователя из системы"""
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'main/profile.html')


def create_allergen(request):
    if request.method == 'POST':
        name_ = request.POST.get("name").strip()
    if not name_:
        messages.error(request, "Название аллергена не может быть пустым")
        return render(request, 'main/create_allergen.html')
    #проверяем, что в базе нет такого аллергена
    if Allergen.objects.filter(name=name_).exists():
        messages.warning(request, "Такой аллерген уже существует")


