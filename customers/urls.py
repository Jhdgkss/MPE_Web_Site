from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("documents/", views.documents, name="documents"),
]
