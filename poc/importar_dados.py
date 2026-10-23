import json
import os
from pathlib import Path
import re

import psycopg
from dotenv import load_dotenv

load_dotenv()

PASTA_PROJETO = Path(__file__).parent
ARQUIVO_PARTIDAS = PASTA_PROJETO / "dados" / "partidas_2026.json"
ARQUIVO_JOGADORES = (
    PASTA_PROJETO / "dados" / "jogadores_2026.json"
)

PASTA_BOX_SCORES = (
    PASTA_PROJETO / "dados" / "box_scores_2026"
)


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


with open(ARQUIVO_PARTIDAS, "r", encoding="utf-8") as arquivo:
    partidas = json.load(arquivo)

primeira_partida = partidas[0]
league = primeira_partida["league"]
country = primeira_partida["country"]

def importar_clubes(cursor, partidas):
    clubes_unicos = {}

    for partida in partidas:
        for campo in ("homeTeam", "awayTeam"):
            clube = partida[campo]
            clubes_unicos[clube["id"]] = clube

    clubes_ids = {}

    for api_id, clube in clubes_unicos.items():
        cursor.execute(
            """
            INSERT INTO clubes (
                api_id,
                nome,
                logo
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (api_id)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                logo = EXCLUDED.logo
            RETURNING id;
            """,
            (
                api_id,
                clube["name"],
                clube["logo"],
            ),
        )

        clubes_ids[api_id] = cursor.fetchone()[0]

    return clubes_ids

def importar_jogadores(cursor):
    jogadores_unicos = {}

    with open(ARQUIVO_JOGADORES, "r", encoding="utf-8") as arquivo:
        jogadores_cadastrados = json.load(arquivo)

    for jogador in jogadores_cadastrados:
        jogadores_unicos[jogador["id"]] = {
            "nome": jogador["nome"],
            "logo": None,
            "posicao_principal": jogador.get("posicao"),
            "possui_nome_completo": False,
        }

    for caminho in sorted(PASTA_BOX_SCORES.glob("*.json")):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            equipes = json.load(arquivo)

        for equipe in equipes:
            for jogador in equipe["players"]:
                api_id = jogador["id"]
                nome_completo = jogador.get("fullName")
                nome_curto = jogador.get("name")
                logo = jogador.get("logo")
                posicao = jogador.get("position")

                if api_id not in jogadores_unicos:
                    jogadores_unicos[api_id] = {
                        "nome": nome_completo or nome_curto,
                        "logo": logo,
                        "posicao_principal": posicao,
                        "possui_nome_completo": bool(nome_completo),
                    }

                else:
                    dados_salvos = jogadores_unicos[api_id]

                    if nome_completo:
                        dados_salvos["nome"] = nome_completo
                        dados_salvos["possui_nome_completo"] = True

                    elif not dados_salvos["nome"]:
                        dados_salvos["nome"] = nome_curto

                    if logo:
                        dados_salvos["logo"] = logo

                    if not dados_salvos["posicao_principal"]:
                        dados_salvos["posicao_principal"] = posicao

    jogadores_ids = {}

    for api_id, jogador in jogadores_unicos.items():
        cursor.execute(
            """
            INSERT INTO jogadores (
                api_id,
                nome,
                logo,
                posicao_principal
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (api_id)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                logo = EXCLUDED.logo,
                posicao_principal = EXCLUDED.posicao_principal
            RETURNING id;
            """,
            (
                api_id,
                jogador["nome"],
                jogador["logo"],
                jogador["posicao_principal"],
            ),
        )

        jogadores_ids[api_id] = cursor.fetchone()[0]

    return jogadores_ids

def extrair_rodada(texto_rodada):
    resultado = re.search(r"(\d+)$", texto_rodada)

    if resultado is None:
        raise ValueError(
            f"Não foi possível identificar a rodada: {texto_rodada}"
        )

    return int(resultado.group(1))


def separar_placar(placar):
    if placar is None:
        return None, None

    partes = placar.split("-")

    if len(partes) != 2:
        raise ValueError(f"Formato de placar inválido: {placar}")

    mandante = int(partes[0].strip())
    visitante = int(partes[1].strip())

    return mandante, visitante

def importar_partidas(
    cursor,
    partidas,
    temporada_id,
    clubes_ids,
):
    partidas_ids = {}

    for partida in partidas:
        estado = partida["state"]
        placar = estado["score"]

        gols_mandante, gols_visitante = separar_placar(
            placar["current"]
        )

        penaltis_mandante, penaltis_visitante = separar_placar(
            placar["penalties"]
        )

        clube_mandante_api_id = partida["homeTeam"]["id"]
        clube_visitante_api_id = partida["awayTeam"]["id"]

        cursor.execute(
            """
            INSERT INTO partidas (
                api_id,
                rodada,
                data_hora,
                clube_mandante_id,
                clube_visitante_id,
                gols_mandante,
                gols_visitante,
                penaltis_mandante,
                penaltis_visitante,
                minuto,
                status_partida,
                temporada_id
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (api_id)
            DO UPDATE SET
                rodada = EXCLUDED.rodada,
                data_hora = EXCLUDED.data_hora,
                clube_mandante_id = EXCLUDED.clube_mandante_id,
                clube_visitante_id = EXCLUDED.clube_visitante_id,
                gols_mandante = EXCLUDED.gols_mandante,
                gols_visitante = EXCLUDED.gols_visitante,
                penaltis_mandante = EXCLUDED.penaltis_mandante,
                penaltis_visitante = EXCLUDED.penaltis_visitante,
                minuto = EXCLUDED.minuto,
                status_partida = EXCLUDED.status_partida,
                temporada_id = EXCLUDED.temporada_id
            RETURNING id;
            """,
            (
                partida["id"],
                extrair_rodada(partida["round"]),
                partida["date"],
                clubes_ids[clube_mandante_api_id],
                clubes_ids[clube_visitante_api_id],
                gols_mandante,
                gols_visitante,
                penaltis_mandante,
                penaltis_visitante,
                estado["clock"],
                estado["description"],
                temporada_id,
            ),
        )

        partidas_ids[partida["id"]] = cursor.fetchone()[0]

    return partidas_ids

def validar_referencias_box_scores(
    partidas_ids,
    clubes_ids,
    jogadores_ids,
):
    total_registros = 0
    partidas_nao_encontradas = set()
    clubes_nao_encontrados = set()
    jogadores_nao_encontrados = set()

    for caminho in sorted(PASTA_BOX_SCORES.glob("*.json")):
        partida_api_id = int(caminho.stem)

        if partida_api_id not in partidas_ids:
            partidas_nao_encontradas.add(partida_api_id)

        with open(caminho, "r", encoding="utf-8") as arquivo:
            equipes = json.load(arquivo)

        for equipe in equipes:
            clube_api_id = equipe["team"]["id"]

            if clube_api_id not in clubes_ids:
                clubes_nao_encontrados.add(clube_api_id)

            for jogador in equipe["players"]:
                total_registros += 1
                jogador_api_id = jogador["id"]

                if jogador_api_id not in jogadores_ids:
                    jogadores_nao_encontrados.add(jogador_api_id)

    return {
        "total_registros": total_registros,
        "partidas_nao_encontradas": partidas_nao_encontradas,
        "clubes_nao_encontrados": clubes_nao_encontrados,
        "jogadores_nao_encontrados": jogadores_nao_encontrados,
    }

def normalizar_nota(valor):
    if valor is None:
        return None

    nota = float(valor)

    if nota < 0:
        raise ValueError(f"Nota negativa encontrada: {nota}")

    if nota > 10:
        return 10.0

    return nota

def importar_jogadores_partidas(
    cursor,
    partidas_ids,
    clubes_ids,
    jogadores_ids,
):
    total_importado = 0

    for caminho in sorted(PASTA_BOX_SCORES.glob("*.json")):
        partida_api_id = int(caminho.stem)
        partida_id = partidas_ids[partida_api_id]

        with open(caminho, "r", encoding="utf-8") as arquivo:
            equipes = json.load(arquivo)

        for equipe in equipes:
            clube_api_id = equipe["team"]["id"]
            clube_id = clubes_ids[clube_api_id]

            for jogador in equipe["players"]:
                estatisticas = jogador["statistics"]

                dados = {
                    "jogador_id": jogadores_ids[jogador["id"]],
                    "partida_id": partida_id,
                    "clube_id": clube_id,
                    "numero_camisa": jogador["shirtNumber"],
                    "posicao_partida": jogador["position"],
                    "nota": normalizar_nota(jogador["matchRating"]),
                    "capitao": jogador["isCaptain"],
                    "minutos_jogados": jogador["minutesPlayed"],
                    "titular": not jogador["isSubstitute"],
                    "impedimentos": jogador["offsides"],
                    "gols": estatisticas["goalsScored"],
                    "defesas": estatisticas["goalsSaved"],
                    "gols_sofridos": estatisticas["goalsConceded"],
                    "assistencias": estatisticas["assists"],
                    "dribles_total": estatisticas["dribblesTotal"],
                    "dribles_bem_sucedidos": (
                        estatisticas["dribblesSuccessful"]
                    ),
                    "faltas_sofridas": estatisticas["fouledByOthers"],
                    "faltas_cometidas": estatisticas["fouledOthers"],
                    "desarmes": estatisticas["tacklesTotal"],
                    "interceptacoes": estatisticas["interceptionsTotal"],
                    "finalizacoes_total": estatisticas["shotsTotal"],
                    "finalizacoes_no_alvo": estatisticas["shotsOnTarget"],
                    "penaltis_cobrados": estatisticas["penaltiesTotal"],
                    "penaltis_convertidos": estatisticas["penaltiesScored"],
                    "passes_total": estatisticas["passesTotal"],
                    "passes_certos": estatisticas["passesSuccessful"],
                    "passes_chave": estatisticas["passesKey"],
                    "cartoes_amarelos": estatisticas["cardsYellow"],
                    "cartoes_vermelhos": estatisticas["cardsRed"],
                    "segundos_amarelos": (
                        1
                        if (
                            estatisticas["cardsYellow"] >= 2
                            and estatisticas["cardsRed"] >= 1
                        )
                        else 0
                    ),
                    "duelos_total": estatisticas["duelsTotal"],
                    "duelos_vencidos": estatisticas["duelsWon"],
                    "xa": estatisticas["expectedAssists"],
                    "xg": estatisticas["expectedGoals"],
                    "xg_no_alvo": estatisticas["expectedGoalsOnTarget"],
                    "xg_no_alvo_sofrido": (
                        estatisticas["expectedGoalsOnTargetConceded"]
                    ),
                    "gols_evitados_esperados": (
                        estatisticas["expectedGoalsPrevented"]
                    ),
                }

                cursor.execute(
                    """
                    INSERT INTO jogador_partida (
                        jogador_id,
                        partida_id,
                        clube_id,
                        numero_camisa,
                        posicao_partida,
                        nota,
                        capitao,
                        minutos_jogados,
                        titular,
                        impedimentos,
                        gols,
                        defesas,
                        gols_sofridos,
                        assistencias,
                        dribles_total,
                        dribles_bem_sucedidos,
                        faltas_sofridas,
                        faltas_cometidas,
                        desarmes,
                        interceptacoes,
                        finalizacoes_total,
                        finalizacoes_no_alvo,
                        penaltis_cobrados,
                        penaltis_convertidos,
                        passes_total,
                        passes_certos,
                        passes_chave,
                        cartoes_amarelos,
                        cartoes_vermelhos,
                        segundos_amarelos,
                        duelos_total,
                        duelos_vencidos,
                        xa,
                        xg,
                        xg_no_alvo,
                        xg_no_alvo_sofrido,
                        gols_evitados_esperados
                    )
                    VALUES (
                        %(jogador_id)s,
                        %(partida_id)s,
                        %(clube_id)s,
                        %(numero_camisa)s,
                        %(posicao_partida)s,
                        %(nota)s,
                        %(capitao)s,
                        %(minutos_jogados)s,
                        %(titular)s,
                        %(impedimentos)s,
                        %(gols)s,
                        %(defesas)s,
                        %(gols_sofridos)s,
                        %(assistencias)s,
                        %(dribles_total)s,
                        %(dribles_bem_sucedidos)s,
                        %(faltas_sofridas)s,
                        %(faltas_cometidas)s,
                        %(desarmes)s,
                        %(interceptacoes)s,
                        %(finalizacoes_total)s,
                        %(finalizacoes_no_alvo)s,
                        %(penaltis_cobrados)s,
                        %(penaltis_convertidos)s,
                        %(passes_total)s,
                        %(passes_certos)s,
                        %(passes_chave)s,
                        %(cartoes_amarelos)s,
                        %(cartoes_vermelhos)s,
                        %(segundos_amarelos)s,
                        %(duelos_total)s,
                        %(duelos_vencidos)s,
                        %(xa)s,
                        %(xg)s,
                        %(xg_no_alvo)s,
                        %(xg_no_alvo_sofrido)s,
                        %(gols_evitados_esperados)s
                    )
                    ON CONFLICT (jogador_id, partida_id)
                    DO UPDATE SET
                        clube_id = EXCLUDED.clube_id,
                        numero_camisa = EXCLUDED.numero_camisa,
                        posicao_partida = EXCLUDED.posicao_partida,
                        nota = EXCLUDED.nota,
                        capitao = EXCLUDED.capitao,
                        minutos_jogados = EXCLUDED.minutos_jogados,
                        titular = EXCLUDED.titular,
                        impedimentos = EXCLUDED.impedimentos,
                        gols = EXCLUDED.gols,
                        defesas = EXCLUDED.defesas,
                        gols_sofridos = EXCLUDED.gols_sofridos,
                        assistencias = EXCLUDED.assistencias,
                        dribles_total = EXCLUDED.dribles_total,
                        dribles_bem_sucedidos =
                            EXCLUDED.dribles_bem_sucedidos,
                        faltas_sofridas = EXCLUDED.faltas_sofridas,
                        faltas_cometidas = EXCLUDED.faltas_cometidas,
                        desarmes = EXCLUDED.desarmes,
                        interceptacoes = EXCLUDED.interceptacoes,
                        finalizacoes_total =
                            EXCLUDED.finalizacoes_total,
                        finalizacoes_no_alvo =
                            EXCLUDED.finalizacoes_no_alvo,
                        penaltis_cobrados =
                            EXCLUDED.penaltis_cobrados,
                        penaltis_convertidos =
                            EXCLUDED.penaltis_convertidos,
                        passes_total = EXCLUDED.passes_total,
                        passes_certos = EXCLUDED.passes_certos,
                        passes_chave = EXCLUDED.passes_chave,
                        cartoes_amarelos =
                            EXCLUDED.cartoes_amarelos,
                        cartoes_vermelhos =
                            EXCLUDED.cartoes_vermelhos,
                        segundos_amarelos =
                            EXCLUDED.segundos_amarelos,
                        duelos_total = EXCLUDED.duelos_total,
                        duelos_vencidos = EXCLUDED.duelos_vencidos,
                        xa = EXCLUDED.xa,
                        xg = EXCLUDED.xg,
                        xg_no_alvo = EXCLUDED.xg_no_alvo,
                        xg_no_alvo_sofrido =
                            EXCLUDED.xg_no_alvo_sofrido,
                        gols_evitados_esperados =
                            EXCLUDED.gols_evitados_esperados;
                    """,
                    dados,
                )

                total_importado += 1

    return total_importado

with conectar() as conexao:
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO competicoes (
                api_id,
                nome,
                logo,
                pais_codigo,
                pais_nome,
                pais_logo
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (api_id)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                logo = EXCLUDED.logo,
                pais_codigo = EXCLUDED.pais_codigo,
                pais_nome = EXCLUDED.pais_nome,
                pais_logo = EXCLUDED.pais_logo
            RETURNING id;
            """,
            (
                league["id"],
                league["name"],
                league["logo"],
                country["code"],
                country["name"],
                country["logo"],
            ),
        )

        competicao_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO temporadas (
                ano,
                competicao_id
            )
            VALUES (%s, %s)
            ON CONFLICT (competicao_id, ano)
            DO UPDATE SET
                ano = EXCLUDED.ano
            RETURNING id;
            """,
            (
                league["season"],
                competicao_id,
            ),
        )

        temporada_id = cursor.fetchone()[0]

        clubes_ids = importar_clubes(cursor, partidas)

        jogadores_ids = importar_jogadores(cursor)

        partidas_ids = importar_partidas(
            cursor,
            partidas,
            temporada_id,
            clubes_ids,
        )

        validacao = validar_referencias_box_scores(
            partidas_ids,
            clubes_ids,
            jogadores_ids,
        )

        total_jogador_partida = importar_jogadores_partidas(
            cursor,
            partidas_ids,
            clubes_ids,
            jogadores_ids,
        )

print("Competição e temporada importadas com sucesso.")
print(f"ID interno da competição: {competicao_id}")
print(f"ID interno da temporada: {temporada_id}")
print(f"Clubes importados: {len(clubes_ids)}")
print(f"Jogadores importados: {len(jogadores_ids)}")
print(f"Partidas importadas: {len(partidas_ids)}")
print("\nValidação das referências:")
print(f"Registros encontrados: {validacao['total_registros']}")
print(
    "Partidas não encontradas: "
    f"{len(validacao['partidas_nao_encontradas'])}"
)
print(
    "Clubes não encontrados: "
    f"{len(validacao['clubes_nao_encontrados'])}"
)
print(
    "Jogadores não encontrados: "
    f"{len(validacao['jogadores_nao_encontrados'])}"
)
print(
    "Registros jogador-partida importados: "
    f"{total_jogador_partida}"
)