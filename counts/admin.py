from django.contrib import admin
from .models import Menu, Product, Share

class ShareTabularInline(admin.TabularInline):
    model = Share

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [ShareTabularInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
