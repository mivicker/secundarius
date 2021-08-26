from django.urls import path
from .views import (edit_broadcast, edit_reply, home, save, save_reply, 
                    text_logs, receive)

urlpatterns = [
    path('texts', home, name='text-home'),
    path('edit', edit_broadcast, name='edit-words'),
    path('edit-reply', edit_reply, name='edit-reply'),
    path('save', save, name='save-words'),
    path('logs/', text_logs, name='logs'),
    path('receive/', receive, name='recieve'),
    path('save-reply/', save_reply, name='save-reply'),
    ]