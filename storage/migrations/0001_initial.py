# Generated by Django 3.2.18 on 2023-04-18 23:46

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Номер бокса')),
                ('floor', models.IntegerField(verbose_name='Этаж')),
                ('width', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))], verbose_name='Ширина')),
                ('length', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))], verbose_name='Длина')),
                ('height', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))], verbose_name='Высота потолка')),
                ('box_area', models.DecimalField(blank=True, decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))], verbose_name='Площадь бокса')),
                ('temperature', models.IntegerField(blank=True, null=True, verbose_name='Температура на складе')),
                ('occupied', models.BooleanField(default=False, verbose_name='Бокс занят')),
                ('monthly_price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена')),
            ],
            options={
                'verbose_name': 'Бокс',
                'verbose_name_plural': 'Боксы',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Название')),
                ('address', models.CharField(max_length=100, unique=True)),
                ('picture', models.ImageField(upload_to='', verbose_name='Фото склада')),
            ],
            options={
                'verbose_name': 'Склад',
                'verbose_name_plural': 'Склады',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rental_period', models.IntegerField(choices=[(3, '3 months'), (6, '6 months'), (12, '12 months')])),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='', verbose_name='QR код для получения заказа')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('delivery_needed', models.BooleanField(default=False, verbose_name='Нужна доставка?')),
                ('measurement_needed', models.BooleanField(default=False, verbose_name='Нужен замер?')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Заказ создан')),
                ('pickup_deadline', models.DateTimeField(blank=True, null=True, verbose_name='Срок хранения')),
                ('total_price', models.IntegerField(blank=True, null=True, verbose_name='Стоимость хранения по тарифу')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('is_finished', models.BooleanField(blank=True, default=False, null=True, verbose_name='Заказ завершен')),
                ('deadline_overdue', models.DateTimeField(blank=True, null=True, verbose_name='Насколько превышен срок хранения')),
                ('extra_payment', models.IntegerField(blank=True, null=True, verbose_name='Оплата просрочки')),
                ('box', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='storage.box', verbose_name='Бокс')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.AddField(
            model_name='box',
            name='storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boxes', to='storage.storage', verbose_name='Склад'),
        ),
        migrations.AlterUniqueTogether(
            name='box',
            unique_together={('storage', 'number')},
        ),
    ]
