import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

url = "https://soccer.highlightly.net/lineups"

headers = {
    "x-rapidapi-key": API_KEY
}

match_id = 1269969359

response = requests.get(
    f"{url}/{match_id}",
    headers=headers
)

print("Status:", response.status_code)

dados = response.json()

#print(dados)

jogadores = []

for grupo in dados["homeTeam"]["initialLineup"]:
    for jogador in grupo:
        jogadores.append(jogador)

jogadores.extend(dados["homeTeam"]["substitutes"])

print("\nJogadores do Flamengo:")

for jogador in jogadores:
    print(
        f'{jogador["id"]} | '
        f'{jogador["name"]} | '
        f'{jogador["position"]} | '
        f'camisa {jogador["number"]}'
    )

print("\nTotal:", len(jogadores))