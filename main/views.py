from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .forms import *
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

def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required, login_url='/login/')
def admin_create_allergen(request):
    if request.method == 'POST':
        form = GlobalAllergenForm(request.POST)
        if form.is_valid():
            allergen = form.save(commit=False)
            allergen.is_global = True
            allergen.created_by = request.user
            allergen.save()
            messages.success(request, f"Глобальный аллерген {allergen.name} успешно добавлен")
            return redirect('admin_create_allergen')
    else:
        form = GlobalAllergenForm()
    global_allergens = Allergen.objects.filter(is_global=True).order_by('name')
    return render(request, 'main/admin_create_allergen.html', {'form': form, 'allergens': global_allergens})


@login_required
def user_create_allergen(request):
    if request.method == 'POST':
        form = UserAllergenForm(request.POST)
        if form.is_valid():
            allergen = form.save(commit=False)
            allergen.is_global = False
            allergen.created_by = request.user
            allergen.save()
            messages.success(request, f"User's allergen {allergen.name} was successfully created")
            return redirect('user_create_allergen')
    else:
        form = UserAllergenForm()
    user_allergens = Allergen.objects.filter(is_global=False).order_by('name')
    return render(request, 'main/user_create_allergen.html', {'form': form, 'allergens': user_allergens})

