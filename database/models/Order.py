"""
Модель заказа.
"""
from django.db import models
from django.utils import timezone

from .Customer import Customer


class Order(models.Model):
    """
    Модель заказа.

    Связывает клиента с набором позиций (OrderItem). Содержит общую сумму,
    статус и даты. PROTECT на клиенте — нельзя удалить клиента с заказами.
    """
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('processing', 'В процессе'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,  # Запрет удаления клиента при наличии заказов
        related_name='orders',
        verbose_name="Клиент"
    )
    order_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата заказа"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Общая сумма",
        default=0
    )
    notes = models.TextField(verbose_name="Примечания", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['customer', 'order_date']),
        ]
        ordering = ['-order_date']  # Свежие заказы первыми

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer}"
