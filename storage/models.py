from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models import F


class Storage(models.Model):
    name = models.CharField('Название', max_length=20)
    address = models.CharField('Адрес', max_length=100, unique=True)
    picture = models.ImageField('Фото склада')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return f'{self.name}: {self.address}'


class BoxQuerySet(models.QuerySet):
    def get_box_area(self):
        return self.annotate(box_size=F('length') * F('width'))


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

    objects = BoxQuerySet.as_manager()

    def __str__(self):
        return f'№{self.number} / этаж: {self.floor} / размеры: {self.length}x{self.width} / высота потолка: {self.height}'


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
    rental_period = models.IntegerField('Период аренды', choices=PERIOD_CHOICES)
    qr_code = models.ImageField('QR код для получения вещей', blank=True, null=True)
    comment = models.TextField('Комментарий по аренде', blank=True, null=True)
    address = models.TextField('Адрес клиента')
    delivery_needed = models.BooleanField('Нужна доставка', default=False)
    measurement_needed = models.BooleanField('Нужен замер', default=False)
    created_at = models.DateTimeField('Дата начала аренды', default=timezone.now)
    pickup_deadline = models.DateTimeField('Дата окончания аренды по тарифу', blank=True, null=True)
    rental_period_price = models.IntegerField('Стоимость хранения по тарифу', blank=True, null=True)
    finished_at = models.DateTimeField('Дата завершения аренды', blank=True, null=True)
    is_finished = models.BooleanField('Хранение завершено', default=False)
    is_rental_extended = models.BooleanField('Аренда продлена', default=False)
    utilize_deadline = models.DateTimeField('Дата утилизации вещей', blank=True, null=True)
    deadline_overdue = models.IntegerField('Дни превышения срока аренды', blank=True, null=True)
    extra_payment = models.IntegerField('Сумма для оплаты просрочки', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def create_qr_code(self):
        # TODO с помощью pip install qrcode
        return 'I am qr_code:3'

    # TODO вычиление deadline_overdue, utilize_deadline и extra_payment

    def save(self, *args, **kwargs):
        if not self.pickup_deadline:
            self.pickup_deadline = self.created_at + timedelta(days=self.rental_period*30)
        if not self.rental_period_price:
            self.rental_period_price = self.box.monthly_price * self.rental_period
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.box.number} / {self.client}'
