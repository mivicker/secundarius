from django.contrib import admin
from .models import Broadcast, Reply


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
	pass


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
	pass
