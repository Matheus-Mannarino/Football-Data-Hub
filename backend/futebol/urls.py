from django.urls import path

from . import views

app_name = "futebol"

urlpatterns = [
    path("classificacao/", views.classificacao, name="classificacao"),
    path("partidas/", views.partidas, name="partidas"),
]