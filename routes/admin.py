from django.contrib import admin
from .models import Depot, Driver


@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    pass

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    pass