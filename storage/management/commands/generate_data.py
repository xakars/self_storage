import os
import random
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from storage.models import Storage, Box


class Command(BaseCommand):
    def handle(self, *args, **options):
        storages = [
            {'name': 'Москва', 'address': 'ул. Рокотова, д. 15', 'picture': 'image11.png', 'big_picture': 'sklad2.jpg'},
            {'name': 'Одинцово', 'address': 'ул. Серверная, д. 36', 'picture': 'image9.png', 'big_picture': 'sklad5.jpg'},
            {'name': 'Пушкино', 'address': 'ул. Строителей, д. 5', 'picture': 'image15.png', 'big_picture': 'sklad4.jpg'},
            {'name': 'Люберцы', 'address': 'ул. Советская, д. 88', 'picture': 'image151.png', 'big_picture': 'sklad3.jpg'},
            {'name': 'Домодедово', 'address': 'ул. Орджоникидзе, д. 29', 'picture': 'image16.png', 'big_picture': 'sklad1.jpg'},
        ]

        for storage in storages:
            new_storage, created = Storage.objects.get_or_create(
                name=storage['name'],
                address=storage['address']
            )
            if created:
                local_file = open(f'{settings.BASE_DIR}/storage/static/img/{storage["picture"]}', "rb")
                djangofile = File(local_file)
                new_storage.picture.save(f'storage/{storage["picture"]}', djangofile)
                local_file.close()
                local_file = open(f'{settings.BASE_DIR}/storage/static/img/{storage["big_picture"]}', "rb")
                djangofile = File(local_file)
                new_storage.big_picture.save(f'storage/{storage["big_picture"]}', djangofile)
                local_file.close()

        storages = Storage.objects.all()

        for storage in storages:
            for item in range(10):
                box = Box.objects.create(
                    storage=storage,
                    number=random.randint(1000,1999),
                    floor=random.randint(1,5),
                    width=random.randint(2,6),
                    length=random.randint(1,10),
                    height=random.randint(100,350)/100.00,
                    temperature=random.randint(15,25)
                )
                box.monthly_price = box.get_box_area() * 539
                box.save()
