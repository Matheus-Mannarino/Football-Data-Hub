import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

url = "https://soccer.highlightly.net/matches"

headers = {
    "x-rapidapi-key": API_KEY
}


def buscar_partidas():
    partidas = []
    offset = 0
    limite = 100

    while True:

        params = {
            "leagueId": 61205,
            "season": 2026,
            "offset": offset
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        print(
            f"Buscando partidas..."
            f"offset = {offset} | status = {response.status_code}"
        )

        dados = response.json()

        novas_partidas = dados["data"]

        partidas.extend(novas_partidas)

        total = dados["pagination"]["totalCount"]

        offset += limite

        if offset >= total:
            break

    return partidas


# Só executa este teste quando rodar teste_matches.py diretamente
if __name__ == "__main__":

    partidas = buscar_partidas()

    print("\nTotal de partidas coletadas:", len(partidas))