from django import forms
from django.contrib.auth.hashers import make_password
from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserAdminForm(forms.ModelForm):
    # Добавляем поле для ввода обычного пароля
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
        # Исключаем hashed_password из формы — оно только для БД
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