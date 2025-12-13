from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
        form = UserAllergenForm(request.POST, user=request.user)
        if form.is_valid():
            allergen = form.save(commit=False)
            allergen.is_global = False
            allergen.created_by = request.user
            allergen.save()
            messages.success(request, f"User's allergen {allergen.name} was successfully created")
            return redirect('user_create_allergen')
    else:
        form = UserAllergenForm(user=request.user)
    user_allergens = Allergen.objects.filter(is_global=False, created_by=request.user).order_by('name')
    return render(request, 'main/user_create_allergen.html', {'form': form, 'allergens': user_allergens})

@login_required
def create_dish(request):
    if request.method == 'POST':
        form = DishForm(request.POST, user=request.user)
        if form.is_valid():
            dish = form.save(commit=False)
            dish.user = request.user
            dish.save()
            form.save_m2m()
            messages.success(request, f"User's dish {dish.name} was successfully created")
            return redirect('create_dish')
    else:
        form = DishForm(user=request.user)
    return render(request, 'main/dish_form.html', {'form': form})


from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Dish
import re
from django.db.models.functions import Lower

class DishesListView(LoginRequiredMixin, ListView):
    template_name = 'main/dishes.html'
    context_object_name = 'dishes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Dish.objects.filter(user=self.request.user)
        
        name = self.request.GET.get('name')
        if name:
            name_lower = name.lower()
            queryset = [
                dish for dish in queryset
                if name_lower in dish.name.lower()
            ]
            from django.db.models import Q
            dish_ids = [dish.id for dish in queryset]
            queryset = Dish.objects.filter(id__in=dish_ids)
        
        queryset = self.apply_sorting(queryset)
        return queryset
    
    def apply_filters(self, queryset):
        name = self.request.GET.get('name')
        if name:
            name_lower = name.lower()
            queryset = queryset.extra(
                where=["LOWER(name) LIKE %s"],
                params=[f'%{name_lower}%']
            )
            return queryset
        filters_map = {
            'calories': ('calories_min', 'calories_max'),
            'proteins': ('protein_min', 'protein_max'),
            'fats': ('fat_min', 'fat_max'),
            'carbohydrates': ('carbs_min', 'carbs_max'),
        }
        
        for field, (min_key, max_key) in filters_map.items():
            min_value = self.request.GET.get(min_key)
            max_value = self.request.GET.get(max_key)
            
            if min_value:
                try:
                    queryset = queryset.filter(**{f'{field}__gte': float(min_value)})
                except (ValueError, TypeError):
                    pass
            
            if max_value:
                try:
                    queryset = queryset.filter(**{f'{field}__lte': float(max_value)})
                except (ValueError, TypeError):
                    pass

        
        created_after = self.request.GET.get('created_after')
        created_before = self.request.GET.get('created_before')
        
        if created_after:
            queryset = queryset.filter(created_at__date__gte=created_after)
        
        if created_before:
            queryset = queryset.filter(created_at__date__lte=created_before)
        
        return queryset
    
    def apply_sorting(self, queryset):
        sort_by = self.request.GET.get('sort_by', '-created_at')
        
        valid_sort_fields = {
            'name', '-name',
            'calories', '-calories',
            'proteins', '-proteins',
            'fats', '-fats',
            'carbohydrates', '-carbohydrates',
            'created_at', '-created_at',
        }
        
        if sort_by in valid_sort_fields:
            return queryset.order_by(sort_by)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        

        for key in ['name', 'calories_min', 'calories_max', 'protein_min', 
                    'protein_max', 'fat_min', 'fat_max', 'carbs_min', 
                    'carbs_max', 'created_after', 'created_before', 'sort_by']:
            context[f'current_{key}'] = self.request.GET.get(key, '')
        
        filtered_dishes = context['dishes']
        if filtered_dishes:
            context['avg_calories'] = sum(d.calories for d in filtered_dishes) / len(filtered_dishes)
            context['avg_protein'] = sum(d.proteins for d in filtered_dishes) / len(filtered_dishes)
            context['avg_fat'] = sum(d.fats for d in filtered_dishes) / len(filtered_dishes)
            context['avg_carbs'] = sum(d.carbohydrates for d in filtered_dishes) / len(filtered_dishes)
        
        context['sort_options'] = [
            {'value': '-created_at', 'label': 'Новые сначала'},
            {'value': 'created_at', 'label': 'Старые сначала'},
            {'value': 'name', 'label': 'Название А-Я'},
            {'value': '-name', 'label': 'Название Я-А'},
            {'value': 'calories', 'label': 'Калории ↑'},
            {'value': '-calories', 'label': 'Калории ↓'},
            {'value': 'protein', 'label': 'Белки ↑'},
            {'value': '-protein', 'label': 'Белки ↓'},
            {'value': 'fat', 'label': 'Жиры ↑'},
            {'value': '-fat', 'label': 'Жиры ↓'},
            {'value': 'carbohydrates', 'label': 'Углеводы ↑'},
            {'value': '-carbohydrates', 'label': 'Углеводы ↓'},
        ]
        
        return context