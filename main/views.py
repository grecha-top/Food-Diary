from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .forms import *
from .models import *


def home(request):
    """
    Отображает главную страницу приложения.
    """
    return render(request, 'main/home.html')


def register_view(request):
    """
    Регистрация нового пользователя.

    При успешной регистрации выполняется автоматический вход в систему.
    """
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
    """
    Аутентификация пользователя.

    Проверяет введённые учётные данные и выполняет вход в систему.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            error = "Неверное имя пользователя или пароль"
            return render(request, 'main/login.html', {'error': error})

    return render(request, 'main/login.html')


def logout_view(request):
    """
    Завершает пользовательскую сессию и выполняет выход из системы.
    """
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    """
    Отображает страницу профиля авторизованного пользователя.
    """
    return render(request, 'main/profile.html')


def staff_required(user):
    """
    Проверяет, является ли пользователь администратором.
    """
    return user.is_staff


@login_required
@user_passes_test(staff_required, login_url='/login/')
def admin_create_allergen(request):
    """
    Создание глобальных аллергенов администратором.

    Доступно только пользователям с правами администратора.
    """
    if request.method == 'POST':
        form = GlobalAllergenForm(request.POST)
        if form.is_valid():
            allergen = form.save(commit=False)
            allergen.is_global = True
            allergen.created_by = request.user
            allergen.save()

            messages.success(
                request,
                f"Глобальный аллерген {allergen.name} успешно добавлен"
            )
            return redirect('admin_create_allergen')
    else:
        form = GlobalAllergenForm()

    global_allergens = Allergen.objects.filter(
        is_global=True
    ).order_by('name')

    return render(
        request,
        'main/admin_create_allergen.html',
        {'form': form, 'allergens': global_allergens}
    )


@login_required
def user_create_allergen(request):
    """
    Создание пользовательских аллергенов.

    Аллергены доступны только их владельцу.
    """
    if request.method == 'POST':
        form = UserAllergenForm(request.POST, user=request.user)
        if form.is_valid():
            allergen = form.save(commit=False)
            allergen.is_global = False
            allergen.created_by = request.user
            allergen.save()

            messages.success(
                request,
                f"Аллерген {allergen.name} успешно создан"
            )
            return redirect('user_create_allergen')
    else:
        form = UserAllergenForm(user=request.user)

    user_allergens = Allergen.objects.filter(
        is_global=False,
        created_by=request.user
    ).order_by('name')

    return render(
        request,
        'main/user_create_allergen.html',
        {'form': form, 'allergens': user_allergens}
    )


@login_required
def create_dish(request):
    """
    Создание нового блюда пользователем.

    Поддерживает загрузку фотографии и выбор аллергенов.
    """
    if request.method == 'POST':
        form = DishForm(
            request.POST,
            request.FILES,
            user=request.user
        )
        if form.is_valid():
            dish = form.save(commit=False)
            dish.user = request.user
            dish.save()
            form.save_m2m()

            messages.success(
                request,
                f"Блюдо «{dish.name}» успешно создано!"
            )
            return redirect('create_dish')
    else:
        form = DishForm(user=request.user)

    return render(
        request,
        'main/dish_form.html',
        {'form': form}
    )


class DishesListView(LoginRequiredMixin, ListView):
    """
    Отображает список блюд пользователя.

    Поддерживает фильтрацию, сортировку и пагинацию.
    """

    template_name = 'main/dishes.html'
    context_object_name = 'dishes'
    paginate_by = 10

    def get_queryset(self):
        """
        Формирует queryset блюд текущего пользователя
        с учётом параметров фильтрации и сортировки.
        """
        queryset = Dish.objects.filter(user=self.request.user)

        name = self.request.GET.get('name')
        if name:
            name_lower = name.lower()
            queryset = [
                dish for dish in queryset
                if name_lower in dish.name.lower()
            ]
            dish_ids = [dish.id for dish in queryset]
            queryset = Dish.objects.filter(id__in=dish_ids)

        queryset = self.apply_sorting(queryset)
        return queryset

    def apply_filters(self, queryset):
        """
        Применяет фильтры по параметрам запроса
        (калории, БЖУ, дата создания).
        """
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
                    queryset = queryset.filter(
                        **{f'{field}__gte': float(min_value)}
                    )
                except (ValueError, TypeError):
                    pass

            if max_value:
                try:
                    queryset = queryset.filter(
                        **{f'{field}__lte': float(max_value)}
                    )
                except (ValueError, TypeError):
                    pass

        created_after = self.request.GET.get('created_after')
        created_before = self.request.GET.get('created_before')

        if created_after:
            queryset = queryset.filter(
                created_at__date__gte=created_after
            )

        if created_before:
            queryset = queryset.filter(
                created_at__date__lte=created_before
            )

        return queryset

    def apply_sorting(self, queryset):
        """
        Применяет сортировку списка блюд.
        """
        sort_by = self.request.GET.get(
            'sort_by',
            '-created_at'
        )

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
        """
        Добавляет дополнительные данные в контекст шаблона,
        включая текущие фильтры и средние значения БЖУ.
        """
        context = super().get_context_data(**kwargs)

        for key in [
            'name', 'calories_min', 'calories_max',
            'protein_min', 'protein_max',
            'fat_min', 'fat_max',
            'carbs_min', 'carbs_max',
            'created_after', 'created_before',
            'sort_by'
        ]:
            context[f'current_{key}'] = self.request.GET.get(key, '')

        filtered_dishes = context['dishes']

        def safe_average(values):
            valid_values = [v for v in values if v is not None]
            return (
                sum(valid_values) / len(valid_values)
                if valid_values else 0
            )

        if filtered_dishes:
            context['avg_calories'] = safe_average(
                d.calories for d in filtered_dishes
            )
            context['avg_protein'] = safe_average(
                d.proteins for d in filtered_dishes
            )
            context['avg_fat'] = safe_average(
                d.fats for d in filtered_dishes
            )
            context['avg_carbs'] = safe_average(
                d.carbohydrates for d in filtered_dishes
            )
        else:
            context['avg_calories'] = 0
            context['avg_protein'] = 0
            context['avg_fat'] = 0
            context['avg_carbs'] = 0

        return context
