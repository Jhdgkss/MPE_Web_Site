from django.urls import path
from . import views

app_name = "staffarea"

urlpatterns = [
    path("", views.staff_home, name="home"),
    path("login/", views.staff_login, name="login"),
]
