"""secundarius URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from texts.views import (edit_broadcast, edit_reply, home, save, save_reply, send, text_logs, 
    receive)
from counts.views import froz_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='text-home'),
    path('send', send, name='text-send'),
    path('edit', edit_broadcast, name='edit-words'),
    path('edit-reply', edit_reply, name='edit-reply'),
    path('save', save, name='save-words'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html'), name='logout'),
    path('logs/', text_logs, name='logs'),
    path('receive/', receive, name='recieve'),
    path('save-reply/', save_reply, name='save-reply'),
    path('froz', froz_view, name='froz'),
]