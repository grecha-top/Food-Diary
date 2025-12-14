from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Allergen, Dish
import os

class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        required=True
    )
    confirm_password = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        exclude = ('hashed_password',)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password or confirm:
            if password != confirm:
                raise forms.ValidationError('Пароли не совпадают!')
            if len(password) < 6:
                raise forms.ValidationError('Пароль должен быть не короче 6 символов.')
        return cleaned_data
    

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Обязательное поле при регистрации"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class GlobalAllergenForm(forms.ModelForm):
    class Meta:
        model = Allergen
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Allergen.objects.filter(name__iexact=name, is_global=True).exists():
            raise forms.ValidationError("Глобальный аллерген с таким названием уже существует.")
        return name
    
class UserAllergenForm(forms.ModelForm):
    class Meta:
        model = Allergen
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Allergen.objects.filter(
            name__iexact=name,
            is_global=False,
            created_by=self.user
        ).exists():
            raise forms.ValidationError("У вас уже есть аллерген с таким названием.")
        return name
    
class DishForm(forms.ModelForm):
    """Форма блюда с выбором нескольких аллергенов и загрузкой фото."""

    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    # Поле для фото с улучшенным виджетом
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': 'image/*',
            'onchange': 'previewImage(this)'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        base_qs = Allergen.objects.filter(is_global=True)
        if user is not None:
            base_qs = Allergen.objects.filter(is_global=True) | Allergen.objects.filter(created_by=user)
        self.fields['allergens'].queryset = base_qs.order_by('name')
        
        # Настройка подсказок
        self.fields['photo'].help_text = 'Загрузите фотографию блюда (JPG, PNG)'
        self.fields['photo'].label = 'Фотография блюда'
        
        
        # Добавляем классы CSS для стилизации
        for field_name, field in self.fields.items():
            if field_name not in ['allergens', 'photo']:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Dish
        fields = ['name', 'description', 'photo', 'calories', 'proteins', 
                 'fats', 'carbohydrates', 'url', 'allergens']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название блюда'}),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Описание блюда...'
            }),
            'calories': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'placeholder': '0.0'
            }),
            'proteins': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'placeholder': '0.0'
            }),
            'fats': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'placeholder': '0.0'
            }),
            'carbohydrates': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'placeholder': '0.0'
            }),
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com/recipe'}),
        }
        labels = {
            'name': 'Название блюда',
            'description': 'Описание',
            'calories': 'Калории',
            'proteins': 'Белки',
            'fats': 'Жиры',
            'carbohydrates': 'Углеводы',
            'url': 'Ссылка на рецепт',
        }
    
    def clean_photo(self):
        """Валидация загружаемого изображения"""
        photo = self.cleaned_data.get('photo')
        
        if photo:
            # Проверка размера файла (максимум 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if photo.size > max_size:
                raise forms.ValidationError(
                    'Файл слишком большой. Максимальный размер 5MB.'
                )
            
            # Проверка типа файла
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp']
            if photo.content_type not in allowed_types:
                raise forms.ValidationError(
                    'Неподдерживаемый формат изображения. Используйте JPG, PNG или GIF.'
                )
            
            # Проверка расширения файла
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    'Неподдерживаемое расширение файла. Используйте .jpg, .jpeg, .png или .gif.'
                )
        
        return photo
    
    def clean_calories(self):
        """Валидация калорий"""
        calories = self.cleaned_data.get('calories')
        if calories is not None and calories < 0:
            raise forms.ValidationError('Калории не могут быть отрицательными')
        return calories
    
    def clean_proteins(self):
        """Валидация белков"""
        proteins = self.cleaned_data.get('proteins')
        if proteins is not None and proteins < 0:
            raise forms.ValidationError('Белки не могут быть отрицательными')
        return proteins
    
    def clean_fats(self):
        """Валидация жиров"""
        fats = self.cleaned_data.get('fats')
        if fats is not None and fats < 0:
            raise forms.ValidationError('Жиры не могут быть отрицательными')
        return fats
    
    def clean_carbohydrates(self):
        """Валидация углеводов"""
        carbohydrates = self.cleaned_data.get('carbohydrates')
        if carbohydrates is not None and carbohydrates < 0:
            raise forms.ValidationError('Углеводы не могут быть отрицательными')
        return carbohydrates