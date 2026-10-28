import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY não encontrada no arquivo .env.")

url = "https://soccer.highlightly.net/standings"

headers = {
    "x-rapidapi-key": API_KEY,
}

params = {
    "leagueId": 61205,
    "season": 2026,
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30,
)

print("Status:", response.status_code)
response.raise_for_status()

dados = response.json()

grupos = dados.get("groups", [])

if not grupos:
    raise RuntimeError("A API não retornou grupos de classificação.")

standings = grupos[0].get("standings", [])

if not standings:
    raise RuntimeError("O primeiro grupo não possui classificação.")

print("\nCLASSIFICAÇÃO - BRASILEIRÃO 2026\n")

for time in standings:
    clube = time["team"]
    total = time["total"]

    api_id = clube["id"]
    nome = clube["name"]
    posicao = time["position"]
    pontos = time["points"]

    jogos = total["games"]
    vitorias = total["wins"]
    empates = total["draws"]
    derrotas = total["loses"]

    gols_marcados = total["scoredGoals"]
    gols_sofridos = total["receivedGoals"]

    saldo = gols_marcados - gols_sofridos
    aproveitamento = pontos / (jogos * 3) * 100 if jogos else 0

    print(
        f"{posicao:2} - {nome:25} "
        f"ID: {api_id} | "
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

print(f"\nTotal de clubes: {len(standings)}")