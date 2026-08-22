import json
from pathlib import Path


PASTA_DADOS = Path(__file__).parent / "dados"

ARQUIVO_JOGADORES = PASTA_DADOS / "jogadores_2026.json"
ARQUIVO_LINEUPS = PASTA_DADOS / "lineups_2026.json"


def carregar_json(caminho):
    """
    Carrega e retorna o conteúdo de um arquivo JSON.
    """

    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        return None

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def conferir_jogadores(jogadores):
    """
    Mostra a quantidade de jogadores cadastrados.
    """

    print("\n1. CADASTRO DE JOGADORES")

    if not isinstance(jogadores, list):
        print("Formato inesperado em jogadores_2026.json.")
        return

    print(f"Total de jogadores cadastrados: {len(jogadores)}")


def conferir_lineups(lineups):
    """
    Mostra quantas escalações de partidas foram armazenadas.
    """

    print("\n2. ESCALAÇÕES ARMAZENADAS")

    if not isinstance(lineups, dict):
        print("Formato inesperado em lineups_2026.json.")
        return

    print(f"Total de partidas com escalação: {len(lineups)}")


def conferir_clubes(jogadores):
    """
    Obtém os nomes dos clubes presentes no cadastro.
    """

    print("\n3. CLUBES ENCONTRADOS")

    clubes = set()

    for jogador in jogadores:
        time = jogador.get("time", {})
        nome_time = time.get("nome")

        if nome_time:
            clubes.add(nome_time)

    clubes_ordenados = sorted(clubes)

    for numero, clube in enumerate(clubes_ordenados, start=1):
        print(f"{numero:02d}. {clube}")

    print(f"\nTotal de clubes encontrados: {len(clubes)}")

    if len(clubes) == 20:
        print("Resultado: os 20 clubes estão presentes.")
    elif len(clubes) < 20:
        print(
            f"Resultado: faltam {20 - len(clubes)} "
            f"clubes no cadastro."
        )
    else:
        print(
            "Resultado: foram encontrados mais de 20 clubes. "
            "Confira se existem clubes de outra competição."
        )


if __name__ == "__main__":
    jogadores = carregar_json(ARQUIVO_JOGADORES)
    lineups = carregar_json(ARQUIVO_LINEUPS)

    if jogadores is None or lineups is None:
        print("\nNão foi possível realizar a validação.")
    else:
        print("=" * 50)
        print("VALIDAÇÃO DOS DADOS DO BRASILEIRÃO 2026")
        print("=" * 50)

        conferir_jogadores(jogadores)
        conferir_lineups(lineups)
        conferir_clubes(jogadores)