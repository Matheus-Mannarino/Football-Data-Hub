import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

url = "https://soccer.highlightly.net/standings"

headers = {
    "x-rapidapi-key": API_KEY
}

params = {
    "leagueId": 61205,
    "season": 2026
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print("Status:", response.status_code)

dados = response.json()

standings = dados["groups"][0]["standings"]

print("\nCLASSIFICAÇÃO - BRASILEIRÃO 2026\n")

for time in standings:
    nome = time["team"]["name"]
    posicao = time["position"]
    pontos = time["points"]

    jogos = time["total"]["games"]
    vitorias = time["total"]["wins"]
    empates = time["total"]["draws"]
    derrotas = time["total"]["loses"]

    gols_marcados = time["total"]["scoredGoals"]
    gols_sofridos = time["total"]["receivedGoals"]

    # Análise própria
    saldo = gols_marcados - gols_sofridos
    aproveitamento = (pontos / (jogos * 3)) * 100

    print(
        f"{posicao:2} - {nome:20} "
        f"{pontos:2} pts | "
        f"{aproveitamento:5.1f}% | "
        f"{jogos:2} J | "
        f"{vitorias:2} V | "
        f"{empates:2} E | "
        f"{derrotas:2} D | "
        f"{gols_marcados:2} GP | "
        f"{gols_sofridos:2} GC | "
        f"SG: {saldo:+3}"
    )