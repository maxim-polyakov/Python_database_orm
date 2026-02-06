"""
Модели базы данных с использованием Django ORM для PostgreSQL.

Один файл — одна модель. Импорт из пакета сохраняет совместимость:
  from database.models import Customer, Product, Order, OrderItem
"""
from .Customer import Customer
from .Product import Product
from .Order import Order
from .OrderItem import OrderItem

__all__ = ['Customer', 'Product', 'Order', 'OrderItem']
