import requests
import os
from dotenv import load_dotenv

from teste_matches import buscar_partidas


load_dotenv()

API_KEY = os.getenv("API_KEY")

url = "https://soccer.highlightly.net/lineups"

headers = {
    "x-rapidapi-key": API_KEY
}


def buscar_jogadores_das_partidas(partidas):

    jogadores = {}

    for i, partida in enumerate(partidas, start=1):

        match_id = partida["id"]

        print(
            f"Buscando escalação "
            f"{i}/{len(partidas)} | partida={match_id}"
        )

        response = requests.get(
            f"{url}/{match_id}",
            headers=headers
        )

        if response.status_code != 200:
            print(
                f"Erro na partida {match_id}: "
                f"{response.status_code}"
            )
            continue

        dados = response.json()

        # Percorre os dois times
        for time in ["homeTeam", "awayTeam"]:

            nome_time = dados[time]["name"]

            # Titulares
            for jogador in dados[time]["initialLineup"]:

                jogador_id = jogador["id"]

                jogadores[jogador_id] = {
                    "id": jogador_id,
                    "nome": jogador["name"],
                    "posicao": jogador["position"],
                    "time": nome_time
                }

            # Reservas
            for jogador in dados[time]["substitutes"]:

                jogador_id = jogador["id"]

                jogadores[jogador_id] = {
                    "id": jogador_id,
                    "nome": jogador["name"],
                    "posicao": jogador["position"],
                    "time": nome_time
                }

    return jogadores


if __name__ == "__main__":

    # Busca as 380 partidas
    partidas = buscar_partidas()

    print(
        f"\nPartidas disponíveis: {len(partidas)}"
    )

    # Busca os jogadores dessas partidas
    jogadores = buscar_jogadores_das_partidas(partidas)

    print(
        f"\nTotal de jogadores encontrados: "
        f"{len(jogadores)}"
    )

    # Mostra alguns jogadores
    print("\nPrimeiros jogadores:")

    for jogador in list(jogadores.values())[:10]:
        print(
            f'{jogador["id"]} | '
            f'{jogador["nome"]} | '
            f'{jogador["posicao"]} | '
            f'{jogador["time"]}'
        )