from django.contrib import admin
from .models import Menu, Item, Share, Substitution, Addition, OutOfStock, Warehouse


class ShareTabularInline(admin.TabularInline):
    model = Share


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [ShareTabularInline]


@admin.register(Item)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    pass


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    pass


@admin.register(Addition)
class AdditionAdmin(admin.ModelAdmin):
    pass


@admin.register(OutOfStock)
class OutAdmin(admin.ModelAdmin):
    pass
