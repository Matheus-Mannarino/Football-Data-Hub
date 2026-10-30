from django.db.models import Max
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Prefetch
from .models import Classificacao, Clubes, Jogadores, JogadorPartida, Partidas, Temporadas


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

def detalhe_partida(request, partida_id):
    partida = get_object_or_404(
        Partidas.objects.select_related(
            "clube_mandante",
            "clube_visitante",
            "temporada__competicao",
        ),
        pk=partida_id,
        temporada__ano=2026,
        temporada__competicao__api_id=61205,
    )

    atuacoes = list(
        JogadorPartida.objects
        .filter(partida=partida)
        .select_related("jogador")
        .order_by("-titular", "numero_camisa", "jogador__nome")
    )

    mandante = [
        atuacao
        for atuacao in atuacoes
        if atuacao.clube_id == partida.clube_mandante_id
    ]

    visitante = [
        atuacao
        for atuacao in atuacoes
        if atuacao.clube_id == partida.clube_visitante_id
    ]

    contexto = {
        "partida": partida,
        "equipes": [
            {
                "clube": partida.clube_mandante,
                "atuacoes": mandante,
            },
            {
                "clube": partida.clube_visitante,
                "atuacoes": visitante,
            },
        ],
    }

    return render(
        request,
        "futebol/detalhe_partida.html",
        contexto,
    )

def detalhe_clube(request, clube_id):
    temporada = get_object_or_404(
        Temporadas.objects.select_related("competicao"),
        ano=2026,
        competicao__api_id=61205,
    )

    partidas_temporada = Partidas.objects.filter(
        temporada=temporada
    )

    clubes_ids = (
        partidas_temporada.order_by()
        .values_list("clube_mandante_id", flat=True)
        .union(
            partidas_temporada.order_by()
            .values_list("clube_visitante_id", flat=True)
        )
    )

    clube = get_object_or_404(
        Clubes.objects.filter(id__in=clubes_ids),
        pk=clube_id,
    )

    classificacao_clube = (
        Classificacao.objects
        .filter(temporada=temporada, clube=clube)
        .first()
    )

    partidas_clube = (
        partidas_temporada
        .filter(
            Q(clube_mandante=clube)
            | Q(clube_visitante=clube)
        )
        .select_related("clube_mandante", "clube_visitante")
    )

    finalizadas = partidas_clube.filter(
        status_partida="Finished"
    )

    atuacoes = JogadorPartida.objects.filter(
        clube=clube,
        partida__temporada=temporada,
        partida__status_partida="Finished",
        minutos_jogados__gt=0,
    )

    jogadores = (
        atuacoes
        .values("jogador_id", "jogador__nome")
        .annotate(
            jogos=Count("partida", distinct=True),
            minutos=Sum("minutos_jogados"),
            gols=Sum("gols"),
            assistencias=Sum("assistencias"),
            nota_media=Avg("nota"),
        )
        .order_by("-minutos", "jogador__nome", "jogador_id")
    )

    partidas_com_atuacoes = (
        atuacoes.order_by()
        .values("partida_id")
        .distinct()
        .count()
    )

    contexto = {
        "temporada": temporada,
        "clube": clube,
        "classificacao_clube": classificacao_clube,
        "ultimos_resultados": finalizadas.order_by(
            "-data_hora", "-id"
        )[:5],
        "proximos_jogos": partidas_clube.filter(
            status_partida="Not started"
        ).order_by("data_hora", "id")[:5],
        "jogadores": jogadores,
        "total_finalizadas": finalizadas.count(),
        "partidas_com_atuacoes": partidas_com_atuacoes,
    }

    return render(
        request,
        "futebol/detalhe_clube.html",
        contexto,
    )

def jogadores(request):
    temporada = get_object_or_404(
        Temporadas.objects.select_related("competicao"),
        ano=2026,
        competicao__api_id=61205,
    )

    busca = request.GET.get("busca", "").strip()
    clube_recebido = request.GET.get("clube", "")
    posicao_recebida = request.GET.get("posicao", "")

    atuacoes = JogadorPartida.objects.filter(
        partida__temporada=temporada,
        partida__status_partida="Finished",
        minutos_jogados__gt=0,
    )

    clubes = list(
        Clubes.objects.filter(
            id__in=atuacoes.order_by().values("clube_id")
        ).order_by("nome")
    )

    jogadores_temporada = Jogadores.objects.filter(
        id__in=atuacoes.order_by().values("jogador_id")
    )

    posicoes = list(
        jogadores_temporada
        .exclude(posicao_principal__isnull=True)
        .exclude(posicao_principal="")
        .order_by("posicao_principal")
        .values_list("posicao_principal", flat=True)
        .distinct()
    )

    clube_selecionado = ""
    posicao_selecionada = ""

    try:
        clube_id = int(clube_recebido)
    except (ValueError, TypeError):
        clube_id = None

    if clube_id in {clube.id for clube in clubes}:
        clube_selecionado = str(clube_id)

        jogadores_temporada = jogadores_temporada.filter(
            id__in=atuacoes.filter(
                clube_id=clube_id
            ).order_by().values("jogador_id")
        )

    if busca:
        jogadores_temporada = jogadores_temporada.filter(
            nome__icontains=busca
        )

    if posicao_recebida in posicoes:
        posicao_selecionada = posicao_recebida

        jogadores_temporada = jogadores_temporada.filter(
            posicao_principal=posicao_recebida
        )

    jogadores_temporada = (
        jogadores_temporada
        .order_by("nome", "id")
        .prefetch_related(
            Prefetch(
                "jogadorpartida_set",
                queryset=atuacoes.select_related("clube").order_by(
                    "clube__nome",
                    "clube_id",
                ),
                to_attr="atuacoes_temporada",
            )
        )
    )

    paginador = Paginator(jogadores_temporada, 25)
    pagina = paginador.get_page(request.GET.get("page"))

    for jogador in pagina.object_list:
        clubes_do_jogador = {
            atuacao.clube_id: atuacao.clube
            for atuacao in jogador.atuacoes_temporada
        }

        jogador.clubes_temporada = sorted(
            clubes_do_jogador.values(),
            key=lambda clube: clube.nome,
        )

    parametros = request.GET.copy()
    parametros.pop("page", None)

    contexto = {
        "temporada": temporada,
        "pagina": pagina,
        "total_jogadores": paginador.count,
        "busca": busca,
        "clubes": clubes,
        "posicoes": posicoes,
        "clube_selecionado": clube_selecionado,
        "posicao_selecionada": posicao_selecionada,
        "filtros_url": parametros.urlencode(),
    }

    return render(
        request,
        "futebol/jogadores.html",
        contexto,
    )

def detalhe_jogador(request, jogador_id):
    temporada = get_object_or_404(
        Temporadas.objects.select_related("competicao"),
        ano=2026,
        competicao__api_id=61205,
    )

    atuacoes_temporada = JogadorPartida.objects.filter(
        partida__temporada=temporada,
        partida__status_partida="Finished",
        minutos_jogados__gt=0,
    )

    jogador = get_object_or_404(
        Jogadores.objects.filter(
            id__in=atuacoes_temporada.order_by().values("jogador_id")
        ),
        pk=jogador_id,
    )

    atuacoes = atuacoes_temporada.filter(jogador=jogador)

    resumo = atuacoes.aggregate(
        jogos=Count("partida", distinct=True),
        minutos=Sum("minutos_jogados"),
        gols=Sum("gols"),
        assistencias=Sum("assistencias"),
        nota_media=Avg("nota"),
        notas_disponiveis=Count("nota"),
        amarelos=Sum("cartoes_amarelos"),
        segundos_amarelos=Sum("segundos_amarelos"),
        vermelhos=Sum("cartoes_vermelhos"),
    )

    clubes = Clubes.objects.filter(
        id__in=atuacoes.order_by().values("clube_id")
    ).order_by("nome")

    historico = (
        atuacoes
        .select_related(
            "clube",
            "partida__clube_mandante",
            "partida__clube_visitante",
        )
        .order_by("-partida__data_hora", "-partida_id")
    )

    paginador = Paginator(historico, 15)
    pagina = paginador.get_page(request.GET.get("page"))

    contexto = {
        "temporada": temporada,
        "jogador": jogador,
        "clubes": clubes,
        "resumo": resumo,
        "pagina": pagina,
    }

    return render(
        request,
        "futebol/detalhe_jogador.html",
        contexto,
    )

def comparacao(request):
    temporada = get_object_or_404(
        Temporadas.objects.select_related("competicao"),
        ano=2026,
        competicao__api_id=61205,
    )

    atuacoes = JogadorPartida.objects.filter(
        partida__temporada=temporada,
        partida__status_partida="Finished",
        minutos_jogados__gt=0,
    )

    jogadores_disponiveis = list(
        Jogadores.objects.filter(
            id__in=atuacoes.order_by().values("jogador_id")
        ).order_by("nome", "id")
    )

    jogadores_por_id = {
        jogador.id: jogador
        for jogador in jogadores_disponiveis
    }

    selecionados = []
    ids_selecionados = []
    erro = ""

    for parametro in ("jogador1", "jogador2"):
        valor = request.GET.get(parametro, "")

        try:
            jogador_id = int(valor)
        except (ValueError, TypeError):
            jogador_id = None

        jogador = jogadores_por_id.get(jogador_id)

        selecionados.append(jogador)
        ids_selecionados.append(str(jogador.id) if jogador else "")

    comparar = "jogador1" in request.GET or "jogador2" in request.GET

    if comparar:
        if not all(selecionados):
            erro = "Selecione dois jogadores válidos."
        elif selecionados[0].id == selecionados[1].id:
            erro = "Selecione jogadores diferentes."

    perfis = []
    linhas = []

    if comparar and not erro:
        for jogador in selecionados:
            resumo = atuacoes.filter(jogador=jogador).aggregate(
                jogos=Count("partida", distinct=True),
                minutos=Sum("minutos_jogados"),
                gols=Sum("gols"),
                assistencias=Sum("assistencias"),
                finalizacoes=Sum("finalizacoes_total"),
                passes_chave=Sum("passes_chave"),
                desarmes=Sum("desarmes"),
                nota_media=Avg("nota"),
                notas_disponiveis=Count("nota"),
            )

            minutos = resumo["minutos"] or 0

            for campo in (
                "gols",
                "assistencias",
                "finalizacoes",
                "passes_chave",
                "desarmes",
            ):
                total = resumo[campo] or 0
                resumo[f"{campo}_90"] = (
                    total * 90 / minutos if minutos else None
                )

            perfis.append({
                "jogador": jogador,
                "resumo": resumo,
            })

        metricas = [
            ("Jogos com atuação", "jogos", 0),
            ("Minutos", "minutos", 0),
            ("Gols", "gols", 0),
            ("Assistências", "assistencias", 0),
            ("Finalizações", "finalizacoes", 0),
            ("Passes-chave", "passes_chave", 0),
            ("Desarmes", "desarmes", 0),
            ("Nota média", "nota_media", 2),
            ("Notas disponíveis", "notas_disponiveis", 0),
            ("Gols por 90 min", "gols_90", 2),
            ("Assistências por 90 min", "assistencias_90", 2),
            ("Finalizações por 90 min", "finalizacoes_90", 2),
            ("Passes-chave por 90 min", "passes_chave_90", 2),
            ("Desarmes por 90 min", "desarmes_90", 2),
        ]

        for rotulo, campo, casas in metricas:
            linhas.append({
                "rotulo": rotulo,
                "valor1": perfis[0]["resumo"][campo],
                "valor2": perfis[1]["resumo"][campo],
                "casas": casas,
            })

    clubes_disponiveis = list(
        Clubes.objects.filter(
            id__in=atuacoes.order_by().values("clube_id")
        ).order_by("nome")
    )

    clubes_por_jogador = {}

    vinculos = (
        atuacoes.order_by()
        .values_list("jogador_id", "clube_id")
        .distinct()
    )

    for jogador_id, clube_id in vinculos:
        clubes_por_jogador.setdefault(jogador_id, []).append(clube_id)

    opcoes_jogadores = [
        {
            "id": jogador.id,
            "nome": jogador.nome,
            "posicao": jogador.posicao_principal or "Não informada",
            "clubes": clubes_por_jogador.get(jogador.id, []),
        }
        for jogador in jogadores_disponiveis
    ]

    posicoes_disponiveis = sorted({
        jogador["posicao"]
        for jogador in opcoes_jogadores
    })

    seletores = [
        {
            "campo": "jogador1",
            "rotulo": "Primeiro jogador",
            "selecionado": ids_selecionados[0],
        },
        {
            "campo": "jogador2",
            "rotulo": "Segundo jogador",
            "selecionado": ids_selecionados[1],
        },
    ]

    dados_grafico = []

    if perfis:
        for rotulo, campo in [
            ("Gols por 90 min", "gols_90"),
            ("Assistências por 90 min", "assistencias_90"),
            ("Finalizações por 90 min", "finalizacoes_90"),
            ("Passes-chave por 90 min", "passes_chave_90"),
            ("Desarmes por 90 min", "desarmes_90"),
        ]:
            dados_grafico.append({
                "rotulo": rotulo,
                "valores": [
                    {
                        "nome": perfil["jogador"].nome,
                        "valor": perfil["resumo"][campo],
                    }
                    for perfil in perfis
                ],
            })

    contexto = {
        "temporada": temporada,
        "jogadores": jogadores_disponiveis,
        "jogador1_id": ids_selecionados[0],
        "jogador2_id": ids_selecionados[1],
        "erro": erro,
        "perfis": perfis,
        "linhas": linhas,
        "clubes_disponiveis": clubes_disponiveis,
        "posicoes_disponiveis": posicoes_disponiveis,
        "opcoes_jogadores": opcoes_jogadores,
        "seletores": seletores,
        "dados_grafico": dados_grafico,
    }

    return render(
        request,
        "futebol/comparacao.html",
        contexto,
    )