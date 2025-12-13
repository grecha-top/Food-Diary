from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Allergen
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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