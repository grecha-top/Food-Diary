from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User, Dish, Allergen
from .forms import UserAdminForm

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('id', 'email', 'login', 'date_registration')
    list_filter = ('date_registration',)
    search_fields = ('id', 'email', 'login')
    readonly_fields = ('date_registration', 'id')
    list_editable = ('email', 'login')

    def save_model(self, request, obj, form, change):
        raw_password = form.cleaned_data.get('password')
        if raw_password:
            obj.hashed_password = make_password(raw_password)
        super().save_model(request, obj, form, change)

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    readonly_fields = ('id',)
    list_editable = ('name',)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'calories', 'proteins', 'fats',
        'carbohydrates', 'created_at', 'show_allergens'
    )
    list_filter = (
        'user', 'created_at', 'allergens'
    )
    search_fields = (
        'name', 'description',
        'user__login', 'user__email'
    )
    readonly_fields = ('id', 'created_at')
    list_editable = (
        'name', 'calories', 'proteins', 'fats', 'carbohydrates'
    )
    filter_horizontal = ('allergens',)  # ← удобный выбор при редактировании

    @admin.display(description='Аллергены')
    def show_allergens(self, obj):
        names = obj.allergens.values_list('name', flat=True)
        return ", ".join(names) if names else "—"


