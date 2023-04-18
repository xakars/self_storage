from django.contrib import admin

from .models import Box, Storage, Order


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    readonly_fields = ('box_area',)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass