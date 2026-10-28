from django.db.models import Max
from django.shortcuts import render

from .models import Classificacao, Partidas, Temporadas


def classificacao(request):
    temporada = (
        Temporadas.objects
        .filter(ano=2026, competicao__api_id=61205)
        .select_related("competicao")
        .first()
    )

    tabela = Classificacao.objects.none()

    if temporada:
        tabela = (
            Classificacao.objects
            .filter(temporada=temporada)
            .select_related("clube")
            .order_by("posicao")
        )

    atualizado_em = tabela.aggregate(
        ultima_atualizacao=Max("atualizado_em")
    )["ultima_atualizacao"]

    contexto = {
        "temporada": temporada,
        "classificacao": tabela,
        "atualizado_em": atualizado_em,
    }

    return render(request, "futebol/classificacao.html", contexto)

def partidas(request):
    temporada = (
        Temporadas.objects
        .filter(ano=2026, competicao__api_id=61205)
        .select_related("competicao")
        .first()
    )

    partidas_temporada = Partidas.objects.none()

    if temporada:
        partidas_temporada = Partidas.objects.filter(
            temporada=temporada
        )

    rodadas = list(
        partidas_temporada
        .order_by("rodada")
        .values_list("rodada", flat=True)
        .distinct()
    )

    opcoes_status = [
        ("Finished", "Encerradas"),
        ("Not started", "Não iniciadas"),
        ("Postponed", "Adiadas"),
    ]

    rodada_recebida = request.GET.get("rodada", "")
    status_recebido = request.GET.get("status", "")

    rodada_selecionada = ""
    status_selecionado = ""

    lista_partidas = partidas_temporada.select_related(
        "clube_mandante",
        "clube_visitante",
    )

    try:
        rodada_numero = int(rodada_recebida)
    except (ValueError, TypeError):
        rodada_numero = None

    if rodada_numero in rodadas:
        rodada_selecionada = str(rodada_numero)
        lista_partidas = lista_partidas.filter(
            rodada=rodada_numero
        )

    status_validos = [valor for valor, rotulo in opcoes_status]

    if status_recebido in status_validos:
        status_selecionado = status_recebido
        lista_partidas = lista_partidas.filter(
            status_partida=status_recebido
        )

    lista_partidas = lista_partidas.order_by(
        "rodada",
        "data_hora",
        "id",
    )

    contexto = {
        "temporada": temporada,
        "partidas": lista_partidas,
        "rodadas": rodadas,
        "opcoes_status": opcoes_status,
        "rodada_selecionada": rodada_selecionada,
        "status_selecionado": status_selecionado,
        "total_filtrado": lista_partidas.count(),
    }

    return render(request, "futebol/partidas.html", contexto)