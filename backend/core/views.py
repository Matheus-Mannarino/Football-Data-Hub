from django.shortcuts import render

from futebol.models import Clubes, Jogadores, Partidas, Temporadas


def home(request):
    temporada = (
        Temporadas.objects
        .filter(ano=2026, competicao__api_id=61205)
        .select_related("competicao")
        .first()
    )

    partidas = Partidas.objects.none()
    total_clubes = 0

    if temporada:
        partidas = (
            Partidas.objects
            .filter(temporada=temporada)
            .select_related("clube_mandante", "clube_visitante")
        )

        clubes_ids = (
            partidas.order_by()
            .values_list("clube_mandante_id", flat=True)
            .union(
                partidas.order_by()
                .values_list("clube_visitante_id", flat=True)
            )
        )

        total_clubes = Clubes.objects.filter(
            id__in=clubes_ids
        ).count()

    contexto = {
        "temporada": temporada,
        "total_clubes": total_clubes,
        "total_jogadores": Jogadores.objects.filter(
            jogadorpartida__partida__temporada=temporada,
            jogadorpartida__minutos_jogados__gt=0,
        ).distinct().count() if temporada else 0,
        "total_partidas": partidas.count(),
        "ultimos_resultados": (
            partidas.filter(status_partida="Finished")
            .order_by("-data_hora", "-id")[:5]
        ),
        "proximos_jogos": (
            partidas.filter(status_partida="Not started")
            .order_by("data_hora", "id")[:5]
        ),
        "total_finalizadas": partidas.filter(
            status_partida="Finished"
        ).count(),
        "total_adiadas": partidas.filter(
            status_partida="Postponed"
        ).count(),
    }

    return render(request, "core/home.html", contexto)

def sobre(request):
    return render(request, "core/sobre.html")