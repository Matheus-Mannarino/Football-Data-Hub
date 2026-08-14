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


# Transformando dados
def transformar_partida(partida):

    placar = partida["state"]["score"]["current"]

    gols_mandante = None
    gols_visitante = None

    if placar:
        gols = placar.split(" - ")

        gols_mandante = int(gols[0])
        gols_visitante = int(gols[1])

    return {
        "id": partida["id"],
        "data": partida["date"],
        "rodada": partida["round"],
        "mandante": partida["homeTeam"]["name"],
        "visitante": partida["awayTeam"]["name"],
        "status": partida["state"]["description"],
        "gols_mandante": gols_mandante,
        "gols_visitante": gols_visitante
    }


# Coletando partidas
partidas = buscar_partidas()


# Transformando todas as partidas
partidas_transformadas = []

for partida in partidas:
    partida_transformada = transformar_partida(partida)
    partidas_transformadas.append(partida_transformada)


# Resultados da coleta
print("\nTotal de partidas coletadas:", len(partidas))
print("Total de partidas transformadas:", len(partidas_transformadas))


# Mostrando uma partida já realizada
print("\nExemplo de partida transformada:")

for partida in partidas_transformadas:

    if partida["status"] != "Not started":
        print(partida)
        break