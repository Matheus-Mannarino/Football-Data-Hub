import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

URL = "https://soccer.highlightly.net/matches"

HEADERS = {
    "x-rapidapi-key": API_KEY
}

LEAGUE_ID = 61205
SEASON = 2026

# Pasta poc/dados
PASTA_DADOS = Path(__file__).parent / "dados"

# Arquivo onde as partidas serão armazenadas
ARQUIVO_PARTIDAS = PASTA_DADOS / "partidas_2026.json"


def salvar_json(caminho, dados):
    """
    Salva os dados recebidos em um arquivo JSON.
    """

    # Cria a pasta caso ela ainda não exista
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def carregar_json(caminho):
    """
    Carrega e retorna um arquivo JSON.
    """

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def buscar_partidas():
    """
    Busca todas as partidas do Brasileirão 2026.

    Como a API retorna até 100 partidas por página,
    serão necessárias aproximadamente quatro requisições.
    """

    partidas = []
    offset = 0
    limite = 100

    while True:
        params = {
            "leagueId": LEAGUE_ID,
            "season": SEASON,
            "limit": limite,
            "offset": offset
        }

        response = requests.get(
            URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        print(
            f"Buscando partidas | "
            f"offset={offset} | "
            f"status={response.status_code}"
        )

        if response.status_code == 429:
            print("\nLimite da API atingido.")
            print("Tente executar novamente após o reset da cota.")
            break

        if response.status_code != 200:
            print("Não foi possível buscar as partidas.")
            print(response.text)
            break

        dados = response.json()

        novas_partidas = dados.get("data", [])

        partidas.extend(novas_partidas)

        paginacao = dados.get("pagination", {})

        total = paginacao.get("totalCount", 0)

        offset += limite

        if offset >= total:
            break

    if partidas:
        salvar_json(ARQUIVO_PARTIDAS, partidas)

        print(
            f"\n{len(partidas)} partidas salvas em:"
            f"\n{ARQUIVO_PARTIDAS}"
        )

    return partidas


def carregar_ou_buscar_partidas():
    """
    Se as partidas já estiverem salvas, utiliza o JSON.

    A API só será consultada caso o arquivo ainda não exista.
    """

    if ARQUIVO_PARTIDAS.exists():
        print("Carregando partidas do arquivo local...")

        return carregar_json(ARQUIVO_PARTIDAS)

    print("Arquivo de partidas não encontrado.")
    print("Consultando a API...")

    return buscar_partidas()


if __name__ == "__main__":
    partidas = carregar_ou_buscar_partidas()

    print("\nTotal de partidas:", len(partidas))