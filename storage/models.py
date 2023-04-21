import qrcode
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Max, Min, Count, Q 
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.base import ContentFile

class CustomUser(AbstractUser):
    phone_number = PhoneNumberField('Номер телефона', region="RU", blank=True)
    avatar = models.ImageField(upload_to='avatar', blank=True)


class StorageQuerySet(models.QuerySet):
    def get_box_count_by_storages(self):
        return self.annotate(num_boxes=Count('boxes'))

    def get_empty_box_count_by_storages(self):
        vacant_boxes = Count('boxes', filter=Q(boxes__occupied=False))
        return self.annotate(num_vacant_boxes=vacant_boxes)

    def get_min_box_price(self):
        return self.aggregate(Min('boxes__monthly_price'))['boxes__monthly_price__min']
                            

class Storage(models.Model):
    name = models.CharField('Название', max_length=20)
    address = models.CharField('Адрес', max_length=100, unique=True)
    picture = models.ImageField('Фото склада', upload_to='storage')
    big_picture = models.ImageField('Фото склада большое', upload_to='storage', blank=True)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    objects = StorageQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}: {self.address}'


class BoxQuerySet(models.QuerySet):
    def get_box_area(self):
        return self.annotate(box_size=F('length') * F('width'))

    def get_max_height(self):
        return self.aggregate(Max('height'))['height__max']


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
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Бокс'
        verbose_name_plural = 'Боксы'
        unique_together = ('storage', 'number')

    objects = BoxQuerySet.as_manager()

    def get_box_area(self):
        return int(self.length * self.width)

    def get_box_size(self):
        if self.length * self.width <= 5:
            return 1
        if self.length * self.width <= 10:
            return 2
        if self.length * self.width > 10:
            return 3

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
    client = models.ForeignKey(
        CustomUser,
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

    def calculate_rental_period_price(self):
        self.rental_period_price = self.box.monthly_price * self.rental_period
        self.save()

    def occupy_box(self):
        box.occupied = True
        box.save()

    def generate_qr_code(self):
        data = f"Box {self.box.number}, rental period {self.rental_period}"
        img = qrcode.make(data)
        filename = f"{self.pk}_qr_code.png"
        qr_code_file = ContentFile(b'')
        img.save(qr_code_file, format='PNG')
        self.qr_code.save(filename, qr_code_file)
    
    # TODO вычиление deadline_overdue, utilize_deadline и extra_payment

    def __str__(self):
        return f'{self.box.number} / {self.client}'
