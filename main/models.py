from django.conf import settings
from django.db import models


class User(models.Model):
    """
    Модель пользователя системы.

    Хранит данные для аутентификации и базовую информацию
    о зарегистрированном пользователе.
    """

    email = models.EmailField(verbose_name='Email', unique=True, null=False)
    login = models.TextField(max_length=100, verbose_name='Логин', unique=True, null=False)
    hashed_password = models.TextField(verbose_name='Зашифрованный пароль', null=False)
    date_registration = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации',
        null=True
    )
    is_staff = models.BooleanField(
        verbose_name='Администратор',
        null=False,
        default=False
    )

    def __str__(self):
        """
        Возвращает строковое представление пользователя.
        Используется в админ-панели и логировании.
        """
        return self.login

    class Meta:
        """Метаданные модели пользователя."""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Allergen(models.Model):
    """
    Модель аллергена.

    Может быть глобальным (доступен всем пользователям)
    или пользовательским (создан конкретным пользователем).
    """

    name = models.TextField(verbose_name='Название аллергена')
    is_global = models.BooleanField(verbose_name='Глобальный аллерген')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Создал'
    )

    def __str__(self):
        """
        Возвращает название аллергена.
        """
        return self.name

    class Meta:
        """Ограничения и отображаемые имена модели аллергена."""
        verbose_name = 'Аллерген'
        verbose_name_plural = 'Аллергены'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'created_by'],
                condition=models.Q(is_global=False),
                name='unique_user_allergen'
            ),
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(is_global=True),
                name='unique_global_allergen'
            )
        ]


class Dish(models.Model):
    """
    Модель блюда.

    Хранит информацию о блюде пользователя, его пищевую ценность,
    список аллергенов и дополнительную информацию.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        null=False
    )
    name = models.TextField(max_length=100, verbose_name='Название блюда', null=False)
    description = models.TextField(
        verbose_name='Описание и комментарии к блюду',
        blank=True,
        null=True
    )
    calories = models.FloatField(verbose_name='Калории', blank=True, null=True)
    proteins = models.FloatField(verbose_name='Белки', blank=True, null=True)
    fats = models.FloatField(verbose_name='Жиры', blank=True, null=True)
    carbohydrates = models.FloatField(verbose_name='Углеводы', blank=True, null=True)
    url = models.URLField(verbose_name='Ссылка на рецепт', blank=True, null=True)
    allergens = models.ManyToManyField(
        Allergen,
        verbose_name='Аллергены',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления блюда'
    )

    photo = models.ImageField(
        upload_to='',
        blank=True,
        null=True,
        verbose_name="Фотография блюда"
    )

    def __str__(self):
        """
        Возвращает название блюда.
        """
        return self.name

    class Meta:
        """Метаданные модели блюда."""
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
