import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

PLAYER_ID = 955367
NOME_JOGADOR = "Alexander Barboza"

URL_BOX_SCORE = (
    "https://soccer.highlightly.net/box-score"
)

HEADERS = {
    "x-rapidapi-key": API_KEY
}

PASTA_DADOS = Path(__file__).parent / "dados"

ARQUIVO_LINEUPS = (
    PASTA_DADOS / "lineups_2026.json"
)


def carregar_json(caminho):
    """
    Carrega um arquivo JSON.
    """

    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        return None

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    """
    Salva dados em um arquivo JSON.
    """

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def jogador_esta_no_time(time, player_id):
    """
    Verifica se o jogador aparece como titular
    ou reserva do time.
    """

    # Titulares: lista de setores,
    # e cada setor contém jogadores
    for setor in time.get(
        "initialLineup",
        []
    ):
        for jogador in setor:
            if jogador.get("id") == player_id:
                return True

    # Reservas: lista simples de jogadores
    for jogador in time.get(
        "substitutes",
        []
    ):
        if jogador.get("id") == player_id:
            return True

    return False


def localizar_partida_do_jogador(
    lineups,
    player_id
):
    """
    Procura uma partida em que o jogador
    apareceu na escalação.
    """

    for match_id_salvo, registro in lineups.items():
        lineup = registro.get(
            "lineup",
            registro
        )

        time_casa = lineup.get(
            "homeTeam",
            {}
        )

        time_fora = lineup.get(
            "awayTeam",
            {}
        )

        esta_em_casa = jogador_esta_no_time(
            time_casa,
            player_id
        )

        esta_fora = jogador_esta_no_time(
            time_fora,
            player_id
        )

        if esta_em_casa or esta_fora:
            match_id = registro.get(
                "matchId",
                match_id_salvo
            )

            return {
                "matchId": int(match_id),
                "round": registro.get("round"),
                "date": registro.get("date"),
                "homeTeam": time_casa.get("name"),
                "awayTeam": time_fora.get("name")
            }

    return None


def consultar_box_score(match_id):
    """
    Consulta o box score de uma partida.
    """

    url = (
        f"{URL_BOX_SCORE}/"
        f"{match_id}"
    )

    print("\nConsultando:")
    print(url)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        return response

    except requests.RequestException as erro:
        print("\nErro de conexão:")
        print(erro)

        return None


def procurar_jogador_no_box_score(
    box_score,
    player_id
):
    """
    Procura o jogador nos dois times
    retornados pelo box score.
    """

    if not isinstance(box_score, list):
        return None

    for registro_time in box_score:
        time = registro_time.get(
            "team",
            {}
        )

        jogadores = registro_time.get(
            "players",
            []
        )

        for jogador in jogadores:
            if jogador.get("id") == player_id:
                return {
                    "time": time,
                    "jogador": jogador
                }

    return None


def mostrar_estatisticas(resultado):
    """
    Exibe as estatísticas do jogador
    encontradas no box score.
    """

    time = resultado["time"]
    jogador = resultado["jogador"]

    print("\nJOGADOR ENCONTRADO NO BOX SCORE")
    print("-" * 60)

    print("Time:", time.get("name"))
    print("ID:", jogador.get("id"))
    print("Nome:", jogador.get("name"))
    print(
        "Nome completo:",
        jogador.get("fullName")
    )
    print(
        "Posição:",
        jogador.get("position")
    )
    print(
        "Número da camisa:",
        jogador.get("shirtNumber")
    )
    print(
        "Minutos:",
        jogador.get("minutesPlayed")
    )
    print(
        "Nota:",
        jogador.get("matchRating")
    )
    print(
        "Foi reserva:",
        jogador.get("isSubstitute")
    )
    print(
        "Foi capitão:",
        jogador.get("isCaptain")
    )
    print(
        "Impedimentos:",
        jogador.get("offsides")
    )

    estatisticas = jogador.get(
        "statistics",
        {}
    )

    if not estatisticas:
        print(
            "\nO jogador foi encontrado, mas não "
            "possui estatísticas detalhadas."
        )

        return

    if isinstance(estatisticas, list):
        dados = estatisticas[0]
    else:
        dados = estatisticas

    print("\nESTATÍSTICAS DETALHADAS")
    print("-" * 60)

    print(
        "Gols:",
        dados.get("goalsScored")
    )
    print(
        "Assistências:",
        dados.get("assists")
    )
    print(
        "Finalizações:",
        dados.get("shotsTotal")
    )
    print(
        "Finalizações no gol:",
        dados.get("shotsOnTarget")
    )
    print(
        "Passes:",
        dados.get("passesTotal")
    )
    print(
        "Passes certos:",
        dados.get("passesSuccessful")
    )
    print(
        "Precisão dos passes:",
        dados.get("passesAccuracy")
    )
    print(
        "Passes-chave:",
        dados.get("passesKey")
    )
    print(
        "Desarmes:",
        dados.get("tacklesTotal")
    )
    print(
        "Interceptações:",
        dados.get("interceptionsTotal")
    )
    print(
        "Duelos:",
        dados.get("duelsTotal")
    )
    print(
        "Duelos vencidos:",
        dados.get("duelsWon")
    )
    print(
        "Cartões amarelos:",
        dados.get("cardsYellow")
    )
    print(
        "Cartões vermelhos:",
        dados.get("cardsRed")
    )
    print(
        "xG:",
        dados.get("expectedGoals")
    )
    print(
        "xA:",
        dados.get("expectedAssists")
    )


def executar_teste():
    """
    Executa o teste completo.
    """

    if not API_KEY:
        print(
            "API_KEY não encontrada no arquivo .env."
        )

        return

    lineups = carregar_json(
        ARQUIVO_LINEUPS
    )

    if lineups is None:
        return

    print(
        f"Procurando uma partida de "
        f"{NOME_JOGADOR}..."
    )

    partida = localizar_partida_do_jogador(
        lineups,
        PLAYER_ID
    )

    if partida is None:
        print(
            "\nO jogador não foi encontrado nas "
            "30 escalações armazenadas."
        )

        return

    print("\nPARTIDA ENCONTRADA")
    print("-" * 60)

    print(
        "Match ID:",
        partida["matchId"]
    )
    print(
        "Rodada:",
        partida["round"]
    )
    print(
        "Data:",
        partida["date"]
    )
    print(
        "Partida:",
        f'{partida["homeTeam"]} x '
        f'{partida["awayTeam"]}'
    )

    response = consultar_box_score(
        partida["matchId"]
    )

    if response is None:
        return

    print(
        "\nStatus:",
        response.status_code
    )

    if response.status_code == 429:
        print("Limite diário da API atingido.")
        return

    if response.status_code != 200:
        print(
            "Não foi possível obter o box score."
        )

        print("\nResposta da API:")
        print(response.text)

        return

    try:
        box_score = response.json()

    except requests.exceptions.JSONDecodeError:
        print(
            "A resposta não contém um JSON válido."
        )

        print(response.text)

        return

    arquivo_box_score = (
        PASTA_DADOS
        / f'box_score_teste_{partida["matchId"]}.json'
    )

    salvar_json(
        arquivo_box_score,
        box_score
    )

    print(
        "\nBox score completo salvo em:"
        f"\n{arquivo_box_score}"
    )

    resultado = procurar_jogador_no_box_score(
        box_score,
        PLAYER_ID
    )

    if resultado is None:
        print(
            f"\n{NOME_JOGADOR} não foi encontrado "
            "no box score da partida."
        )

        if isinstance(box_score, list):
            total_jogadores = sum(
                len(
                    registro.get("players", [])
                )
                for registro in box_score
            )

            print(
                "Total de jogadores retornados:",
                total_jogadores
            )

        return

    mostrar_estatisticas(
        resultado
    )


if __name__ == "__main__":
    executar_teste()