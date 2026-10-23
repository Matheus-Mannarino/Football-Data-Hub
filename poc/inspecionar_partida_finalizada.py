import json
from pathlib import Path
from pprint import pprint

arquivo_partidas = (
    Path(__file__).parent
    / "dados"
    / "partidas_2026.json"
)

with open(arquivo_partidas, "r", encoding="utf-8") as arquivo:
    partidas = json.load(arquivo)

partida_finalizada = next(
    partida
    for partida in partidas
    if partida["state"]["description"].lower() == "finished"
)

pprint(partida_finalizada, sort_dicts=False)