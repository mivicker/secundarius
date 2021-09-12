from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from users.views import change_password
from routes.views import landing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name='login'),
    path('', landing, name='home'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html'), name='logout'),
    path('routes/', include('routes.urls')),
    path('texts/', include('texts.urls')),
    path('change-password', change_password, name='change-password'),
]

if 'survey' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('survey/', include('survey.urls'))
    ]