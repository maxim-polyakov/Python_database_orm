"""
Модель позиции в заказе (элемент заказа).
"""
from django.db import models
from django.core.validators import MinValueValidator

from .Order import Order
from .Product import Product


class OrderItem(models.Model):
    """
    Модель позиции в заказе (одна строка заказа).

    Связывает заказ и товар, хранит количество и цены. Один и тот же товар
    в одном заказе может быть только в одной позиции (unique_together).
    total_price пересчитывается в save().
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,  # При удалении заказа удаляются и позиции
        related_name='items',
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # Не удалять товар, на который есть заказы
        verbose_name="Товар"
    )
    quantity = models.IntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единицу"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Общая стоимость"
    )

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = ['order', 'product']  # Один товар — одна строка в заказе

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем общую стоимость позиции
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
