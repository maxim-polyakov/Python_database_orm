"""
Модель товара (номенклатура).
"""
from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Модель товара (номенклатура).

    Описывает товар: название, категория, цена, остаток на складе.
    Артикул (sku) уникален. Неактивные товары (is_active=False) можно скрывать из каталога.
    """
    # Допустимые значения категории (внутренний код — отображаемое название)
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда'),
        ('books', 'Книги'),
        ('food', 'Продукты'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=200, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        validators=[MinValueValidator(0)]  # Цена не может быть отрицательной
    )
    quantity = models.IntegerField(
        verbose_name="Количество на складе",
        validators=[MinValueValidator(0)],
        default=0
    )
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
