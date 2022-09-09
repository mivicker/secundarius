from django.contrib import admin
from map.models import Location, Partner, Site


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    pass
