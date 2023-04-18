from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Storage(models.Model):
    name = models.CharField('Название', max_length=20)
    address = models.CharField(max_length=100, unique=True)
    picture = models.ImageField('Фото склада')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return f'{self.name}: {self.address}'


class Box(models.Model):
    storage = models.ForeignKey(
        Storage,
        verbose_name='Склад',
        related_name='boxes',
        on_delete=models.CASCADE,
    )
    number = models.PositiveIntegerField(
        'Номер бокса',
        validators=[MinValueValidator(1)]
    )
    floor = models.IntegerField('Этаж')
    width = models.DecimalField(
        'Ширина',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    length = models.DecimalField(
        'Длина',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    height = models.DecimalField(
        'Высота потолка',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    box_area = models.DecimalField(
        'Площадь бокса',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1'))],
        blank=True
    )
    temperature = models.IntegerField(
        'Температура на складе',
        blank=True,
        null=True
    )
    occupied = models.BooleanField('Бокс занят', default=False)
    monthly_price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Боксы'
        unique_together = ('storage', 'number')

    def save(self, *args, **kwargs):
        self.box_area = self.length * self.width
        super().save(*args, **kwargs)

    def __str__(self):
        return f'№{self.number} / этаж: {self.floor} / площадь: {self.box_area} / высота потолка: {self.height}'


class Order(models.Model):
    PERIOD_CHOICES = (
        (3, '3 months'),
        (6, '6 months'),
        (12, '12 months'),
    )
    box = models.ForeignKey(
        Box,
        related_name='orders',
        verbose_name='Бокс',
        on_delete=models.SET_NULL,
        null=True
    )
    # не получится использовать модель User, нужен номер телефона
    client = models.ForeignKey(
        User,
        related_name='orders',
        verbose_name='Клиент',
        on_delete=models.SET_NULL,
        null=True
    )
    rental_period = models.IntegerField(choices=PERIOD_CHOICES)
    qr_code = models.ImageField('QR код для получения заказа', blank=True, null=True)
    comment = models.TextField('Комментарий к заказу', blank=True, null=True)
    address = models.TextField('Адрес')
    delivery_needed = models.BooleanField('Нужна доставка?', default=False)
    measurement_needed = models.BooleanField('Нужен замер?', default=False)
    created_at = models.DateTimeField('Заказ создан', default=timezone.now)
    pickup_deadline = models.DateTimeField('Срок хранения', blank=True, null=True)
    total_price = models.IntegerField('Стоимость хранения по тарифу', blank=True, null=True)
    finished_at = models.DateTimeField('Дата завершения', blank=True, null=True)
    is_finished = models.BooleanField('Заказ завершен', default=False, null=True, blank=True)
    deadline_overdue = models.DateTimeField('Насколько превышен срок хранения', blank=True, null=True)
    extra_payment = models.IntegerField('Оплата просрочки', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def save(self, *args, **kwargs):
        self.pickup_deadline = self.created_at + timedelta(days=self.rental_period*30)
        self.total_price = self.box.monthly_price * self.rental_period
        # TODO вычиление deadline_overdue и extra_payment, сделать qr-код
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.box.number} / {self.client}'
