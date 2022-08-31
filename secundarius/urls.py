from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from users.views import change_password
from routes.views import landing
from counts.views import (
    additions_table,
    invoice,
    post_invoice,
    sharepoint_error,
    stockouts_table,
    additions_table,
    substitutions_table,
)
from map.views import place_map, show_map

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("", landing, name="home"),
    path("zips/", place_map, name="zips"),
    path("map/", show_map, name="map"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path("routes/", include("routes.urls")),
    path("texts/", include("texts.urls")),
    path("change-password", change_password, name="change-password"),
    path("invoice", invoice, name="invoice"),
    path("post-invoice", post_invoice, name="post-invoice"),
    path("sharepoint-error", sharepoint_error, name="sharepoint_error"),
    path("stockouts", stockouts_table, name="stockouts"),
    path("substitutions", substitutions_table, name="substitutions"),
    path("additions", additions_table, name="additions"),
]
