import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

PLAYER_ID = 955367
NOME_JOGADOR = "Alexander Barboza"

URL = (
    f"https://soccer.highlightly.net/players/"
    f"{PLAYER_ID}/statistics"
)

HEADERS = {
    "x-rapidapi-key": API_KEY
}

PASTA_DADOS = Path(__file__).parent / "dados"

ARQUIVO_DIAGNOSTICO = (
    PASTA_DADOS / "diagnostico_alexander_barboza.json"
)


def salvar_json(caminho, dados):
    """
    Salva os dados em um arquivo JSON.
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


def obter_dados_do_jogador(dados):
    """
    Obtém o objeto principal do jogador.

    A API normalmente retorna uma lista
    contendo um objeto.
    """

    if not dados:
        return None

    if isinstance(dados, list):
        if not dados:
            return None

        return dados[0]

    if isinstance(dados, dict):
        return dados

    return None


def mostrar_competicoes(jogador):
    """
    Exibe todas as competições retornadas
    pela API para o jogador.
    """

    competicoes = jogador.get(
        "perCompetition",
        []
    )

    print("\nCOMPETIÇÕES RETORNADAS")

    print(
        "Quantidade de competições:",
        len(competicoes)
    )

    if not competicoes:
        print(
            "\nA API não retornou estatísticas "
            "por competição para este jogador."
        )

        return

    for numero, competicao in enumerate(
        competicoes,
        start=1
    ):
        print("-" * 60)

        print("Registro:", numero)
        print("Clube:", competicao.get("club"))
        print("Liga:", competicao.get("league"))
        print(
            "Temporada:",
            competicao.get("season")
        )
        print("Tipo:", competicao.get("type"))
        print(
            "Partidas:",
            competicao.get("gamesPlayed")
        )
        print(
            "Minutos:",
            competicao.get("minutesPlayed")
        )
        print("Gols:", competicao.get("goals"))
        print(
            "Assistências:",
            competicao.get("assists")
        )
        print(
            "Cartões amarelos:",
            competicao.get("yellowCards")
        )
        print(
            "Cartões vermelhos:",
            competicao.get("redCards")
        )


def executar_diagnostico():
    """
    Consulta e analisa as estatísticas
    de Alexander Barboza.
    """

    if not API_KEY:
        print(
            "A variável API_KEY não foi encontrada "
            "no arquivo .env."
        )

        return

    print(
        f"Consultando {NOME_JOGADOR}..."
    )

    print("ID:", PLAYER_ID)

    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=30
        )

    except requests.RequestException as erro:
        print("\nErro de conexão com a API:")
        print(erro)

        return

    print("\nStatus:", response.status_code)

    if response.status_code == 429:
        print("Limite diário da API atingido.")
        return

    if response.status_code != 200:
        print(
            "Não foi possível consultar "
            "as estatísticas."
        )

        print("\nResposta da API:")
        print(response.text)

        return

    try:
        dados = response.json()

    except requests.exceptions.JSONDecodeError:
        print(
            "A resposta da API não contém "
            "um JSON válido."
        )

        print(response.text)

        return

    # Salva a resposta completa antes de analisar
    salvar_json(
        ARQUIVO_DIAGNOSTICO,
        dados
    )

    jogador = obter_dados_do_jogador(
        dados
    )

    if jogador is None:
        print(
            "\nA API retornou uma resposta vazia "
            "ou em formato inesperado."
        )

        print(
            "\nResposta salva em:"
            f"\n{ARQUIVO_DIAGNOSTICO}"
        )

        return

    print("\nDADOS DO JOGADOR")

    print("ID:", jogador.get("id"))
    print("Nome:", jogador.get("name"))
    print(
        "Nome completo:",
        jogador.get("fullName")
    )

    print(
        "\nCampos retornados pela API:",
        list(jogador.keys())
    )

    mostrar_competicoes(jogador)

    print(
        "\nResposta completa salva em:"
        f"\n{ARQUIVO_DIAGNOSTICO}"
    )


if __name__ == "__main__":
    executar_diagnostico()