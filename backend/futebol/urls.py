from django.urls import path

from . import views

app_name = "futebol"

urlpatterns = [
    path("classificacao/", views.classificacao, name="classificacao"),
    path("partidas/", views.partidas, name="partidas"),
    path("partidas/<int:partida_id>/", views.detalhe_partida, name="detalhe_partida"),
    path("clubes/<int:clube_id>/", views.detalhe_clube, name="detalhe_clube"),
    path("jogadores/", views.jogadores, name="jogadores"),
    path("jogadores/<int:jogador_id>/", views.detalhe_jogador, name="detalhe_jogador"),
    path("comparacao/", views.comparacao, name="comparacao"),
]