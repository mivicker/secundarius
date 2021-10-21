from django.contrib import admin
from .models import Menu, Item, Share

class ShareTabularInline(admin.TabularInline):
    model = Share

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [ShareTabularInline]

@admin.register(Item)
class ProductAdmin(admin.ModelAdmin):
    pass
