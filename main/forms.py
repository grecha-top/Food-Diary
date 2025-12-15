from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Allergen, Dish
import os

class UserAdminForm(forms.ModelForm):
    """
    Форма для управления пользователями в админ-панели.

    Обеспечивает ввод и проверку пароля с подтверждением.
    """

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
        """Метаданные формы администратора пользователя."""
        model = User
        fields = '__all__'
        exclude = ('hashed_password',)

    def clean(self):
        """
        Проверяет совпадение и минимальную длину пароля.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password or confirm:
            if password != confirm:
                raise forms.ValidationError('Пароли не совпадают!')
            if len(password) < 6:
                raise forms.ValidationError(
                    'Пароль должен быть не короче 6 символов.'
                )

        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """
    Кастомная форма регистрации пользователя.

    Добавляет обязательное поле email.
    """

    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Обязательное поле при регистрации"
    )

    class Meta:
        """Настройки формы регистрации пользователя."""
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """
        Сохраняет пользователя с указанным email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class GlobalAllergenForm(forms.ModelForm):
    """
    Форма создания глобального аллергена.

    Доступна администраторам системы.
    """

    class Meta:
        model = Allergen
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
        }

    def clean_name(self):
        """
        Проверяет уникальность глобального аллергена.
        """
        name = self.cleaned_data['name'].strip()
        if Allergen.objects.filter(
            name__iexact=name,
            is_global=True
        ).exists():
            raise forms.ValidationError(
                "Глобальный аллерген с таким названием уже существует."
            )
        return name


class UserAllergenForm(forms.ModelForm):
    """
    Форма создания пользовательского аллергена.

    Аллерген привязывается к текущему пользователю.
    """

    class Meta:
        model = Allergen
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
        }

    def __init__(self, *args, **kwargs):
        """
        Принимает пользователя для проверки уникальности аллергенов.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        """
        Проверяет, что пользовательский аллерген уникален
        для текущего пользователя.
        """
        name = self.cleaned_data['name'].strip()
        if Allergen.objects.filter(
            name__iexact=name,
            is_global=False,
            created_by=self.user
        ).exists():
            raise forms.ValidationError(
                "У вас уже есть аллерген с таким названием."
            )
        return name


class DishForm(forms.ModelForm):
    """
    Форма создания и редактирования блюда.

    Поддерживает выбор аллергенов и загрузку изображения.
    """

    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': 'image/*',
            'onchange': 'previewImage(this)'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        """
        Инициализирует форму и настраивает список аллергенов
        в зависимости от пользователя.
        """
        super().__init__(*args, **kwargs)

        base_qs = Allergen.objects.filter(is_global=True)
        if user is not None:
            base_qs = (
                Allergen.objects.filter(is_global=True) |
                Allergen.objects.filter(created_by=user)
            )

        self.fields['allergens'].queryset = base_qs.order_by('name')

        self.fields['photo'].help_text = (
            'Загрузите фотографию блюда (JPG, PNG)'
        )
        self.fields['photo'].label = 'Фотография блюда'

        for field_name, field in self.fields.items():
            if field_name not in ['allergens', 'photo']:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        """Метаданные формы блюда."""
        model = Dish
        fields = [
            'name', 'description', 'photo', 'calories',
            'proteins', 'fats', 'carbohydrates',
            'url', 'allergens'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Название блюда'}
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Описание блюда...'
                }
            ),
            'calories': forms.NumberInput(
                attrs={'step': '0.1', 'min': '0', 'placeholder': '0.0'}
            ),
            'proteins': forms.NumberInput(
                attrs={'step': '0.1', 'min': '0', 'placeholder': '0.0'}
            ),
            'fats': forms.NumberInput(
                attrs={'step': '0.1', 'min': '0', 'placeholder': '0.0'}
            ),
            'carbohydrates': forms.NumberInput(
                attrs={'step': '0.1', 'min': '0', 'placeholder': '0.0'}
            ),
            'url': forms.URLInput(
                attrs={'placeholder': 'https://example.com/recipe'}
            ),
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
        """
        Валидирует загружаемое изображение блюда.
        """
        photo = self.cleaned_data.get('photo')

        if photo:
            max_size = 5 * 1024 * 1024  # 5MB
            if photo.size > max_size:
                raise forms.ValidationError(
                    'Файл слишком большой. Максимальный размер 5MB.'
                )

            allowed_types = [
                'image/jpeg', 'image/png',
                'image/jpg', 'image/gif', 'image/webp'
            ]
            if photo.content_type not in allowed_types:
                raise forms.ValidationError(
                    'Неподдерживаемый формат изображения.'
                )

            valid_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.webp'
            ]
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    'Неподдерживаемое расширение файла.'
                )

        return photo

    def clean_calories(self):
        """
        Проверяет, что значение калорий не отрицательное.
        """
        calories = self.cleaned_data.get('calories')
        if calories is not None and calories < 0:
            raise forms.ValidationError(
                'Калории не могут быть отрицательными'
            )
        return calories

    def clean_proteins(self):
        """
        Проверяет, что значение белков не отрицательное.
        """
        proteins = self.cleaned_data.get('proteins')
        if proteins is not None and proteins < 0:
            raise forms.ValidationError(
                'Белки не могут быть отрицательными'
            )
        return proteins

    def clean_fats(self):
        """
        Проверяет, что значение жиров не отрицательное.
        """
        fats = self.cleaned_data.get('fats')
        if fats is not None and fats < 0:
            raise forms.ValidationError(
                'Жиры не могут быть отрицательными'
            )
        return fats

    def clean_carbohydrates(self):
        """
        Проверяет, что значение углеводов не отрицательное.
        """
        carbohydrates = self.cleaned_data.get('carbohydrates')
        if carbohydrates is not None and carbohydrates < 0:
            raise forms.ValidationError(
                'Углеводы не могут быть отрицательными'
            )
        return carbohydrates

