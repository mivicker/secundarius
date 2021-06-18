from django.contrib import admin
from .models import Words

@admin.register(Words)
class WordsAdmin(admin.ModelAdmin):
	pass