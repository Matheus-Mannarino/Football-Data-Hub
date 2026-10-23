import json
from pathlib import Path
from pprint import pprint

arquivo_jogadores = (
    Path(__file__).parent
    / "dados"
    / "jogadores_2026.json"
)

with open(arquivo_jogadores, "r", encoding="utf-8") as arquivo:
    jogadores = json.load(arquivo)

print(f"Tipo principal: {type(jogadores).__name__}")
print(f"Quantidade de registros: {len(jogadores)}")
print("\nPrimeiro jogador:")
pprint(jogadores[0], sort_dicts=False)