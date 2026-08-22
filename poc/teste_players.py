import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from teste_matches import carregar_ou_buscar_partidas


load_dotenv()

API_KEY = os.getenv("API_KEY")

URL_LINEUPS = "https://soccer.highlightly.net/lineups"

HEADERS = {
    "x-rapidapi-key": API_KEY
}

PASTA_DADOS = Path(__file__).parent / "dados"

ARQUIVO_LINEUPS = PASTA_DADOS / "lineups_2026.json"
ARQUIVO_JOGADORES = PASTA_DADOS / "jogadores_2026.json"

# Limite de novas consultas por execução
MAX_REQUISICOES = 35


def salvar_json(caminho, dados):
    """
    Salva dados em um arquivo JSON.
    """

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def carregar_json(caminho, valor_padrao):
    """
    Carrega um arquivo JSON.

    Se ele ainda não existir, retorna o valor padrão.
    """

    if not caminho.exists():
        return valor_padrao

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def extrair_numero_rodada(nome_rodada):
    """
    Extrai o número do final do campo round.

    Exemplo:
    'Regular Season - 10' -> 10
    """

    if not nome_rodada:
        return None

    resultado = re.search(r"(\d+)$", nome_rodada)

    if resultado:
        return int(resultado.group(1))

    return None


def data_da_partida(partida):
    """
    Converte a data da API em um objeto datetime.
    """

    data = partida.get("date")

    if not data:
        return None

    return datetime.fromisoformat(
        data.replace("Z", "+00:00")
    )


def agrupar_partidas_por_rodada(partidas):
    """
    Organiza as partidas pelo número da rodada.
    """

    rodadas = {}

    for partida in partidas:
        numero = extrair_numero_rodada(
            partida.get("round")
        )

        if numero is None:
            continue

        if numero not in rodadas:
            rodadas[numero] = []

        rodadas[numero].append(partida)

    return rodadas


def selecionar_tres_rodadas(partidas):
    """
    Seleciona três rodadas completas já disputadas:

    - primeira rodada completa;
    - rodada intermediária;
    - rodada completa mais recente.
    """

    rodadas = agrupar_partidas_por_rodada(partidas)

    agora = datetime.now(timezone.utc)

    rodadas_disputadas = {}

    for numero, partidas_da_rodada in rodadas.items():

        # Uma rodada completa do Brasileirão possui 10 partidas
        if len(partidas_da_rodada) < 10:
            continue

        todas_ja_aconteceram = True

        for partida in partidas_da_rodada:
            data = data_da_partida(partida)

            if data is None or data > agora:
                todas_ja_aconteceram = False
                break

        if todas_ja_aconteceram:
            rodadas_disputadas[numero] = partidas_da_rodada

    numeros = sorted(rodadas_disputadas.keys())

    if not numeros:
        print("Nenhuma rodada completa disputada foi encontrada.")
        return []

    primeira = numeros[0]
    intermediaria = numeros[len(numeros) // 2]
    ultima = numeros[-1]

    numeros_selecionados = list(
        dict.fromkeys([
            primeira,
            intermediaria,
            ultima
        ])
    )

    print(
        "\nRodadas selecionadas:",
        numeros_selecionados
    )

    partidas_selecionadas = []

    for numero in numeros_selecionados:
        partidas_selecionadas.extend(
            rodadas_disputadas[numero]
        )

    return partidas_selecionadas


def buscar_lineups(partidas):
    """
    Consulta as escalações das partidas selecionadas.

    As respostas são armazenadas depois de cada requisição.
    Dessa forma, o programa pode continuar de onde parou.
    """

    lineups_salvas = carregar_json(
        ARQUIVO_LINEUPS,
        {}
    )

    novas_requisicoes = 0

    for indice, partida in enumerate(partidas, start=1):
        match_id = partida["id"]
        match_id_texto = str(match_id)

        # Não consulta novamente uma escalação já salva
        if match_id_texto in lineups_salvas:
            print(
                f"{indice}/{len(partidas)} | "
                f"Partida {match_id} já está salva."
            )

            continue

        if novas_requisicoes >= MAX_REQUISICOES:
            print("\nLimite definido para esta execução atingido.")
            break

        print(
            f"{indice}/{len(partidas)} | "
            f"Buscando escalação da partida {match_id}"
        )

        response = requests.get(
            f"{URL_LINEUPS}/{match_id}",
            headers=HEADERS,
            timeout=30
        )

        novas_requisicoes += 1

        if response.status_code == 429:
            print("\nLimite diário da API atingido.")
            print("Os resultados já obtidos foram salvos.")
            break

        if response.status_code != 200:
            print(
                f"Erro na partida {match_id}: "
                f"{response.status_code}"
            )

            continue

        dados = response.json()

        # Só salva se a resposta tiver os dois times
        if "homeTeam" not in dados or "awayTeam" not in dados:
            print(
                f"A partida {match_id} não possui "
                f"escalação disponível."
            )

            continue

        lineups_salvas[match_id_texto] = {
            "matchId": match_id,
            "round": partida.get("round"),
            "date": partida.get("date"),
            "lineup": dados
        }

        # Salva imediatamente após cada resposta
        salvar_json(
            ARQUIVO_LINEUPS,
            lineups_salvas
        )

    print(
        f"\nNovas requisições realizadas: "
        f"{novas_requisicoes}"
    )

    print(
        f"Escalações armazenadas: "
        f"{len(lineups_salvas)}"
    )

    return lineups_salvas

def adicionar_jogador(
    jogadores,
    jogador,
    time,
    match_id,
    rodada,
    tipo_escalacao
):
    """
    Adiciona ou atualiza um jogador no cadastro.

    O ID do jogador é utilizado para eliminar duplicações.
    """

    jogador_id = jogador.get("id")

    # Ignora registros que não possuem ID
    if jogador_id is None:
        return

    jogador_id_texto = str(jogador_id)

    if jogador_id_texto not in jogadores:
        jogadores[jogador_id_texto] = {
            "id": jogador_id,
            "nome": jogador.get("name"),
            "posicao": jogador.get("position"),
            "numero": jogador.get("number"),
            "time": {
                "id": time.get("id"),
                "nome": time.get("name")
            },
            "aparicoes_lineup": []
        }

    aparicao = {
        "matchId": match_id,
        "rodada": rodada,
        "tipo": tipo_escalacao
    }

    # Evita repetir a mesma aparição
    if aparicao not in jogadores[jogador_id_texto]["aparicoes_lineup"]:
        jogadores[jogador_id_texto]["aparicoes_lineup"].append(
            aparicao
        )


def extrair_jogadores(lineups_salvas):
    """
    Percorre todas as escalações salvas e monta
    o cadastro único dos jogadores.
    """

    jogadores = {}

    for registro in lineups_salvas.values():
        match_id = registro["matchId"]
        rodada = registro.get("round")
        lineup = registro["lineup"]

        for lado in ["homeTeam", "awayTeam"]:
            time = lineup.get(lado, {})

            # initialLineup contém listas dentro de listas:
            # goleiro, defesa, meio e ataque
            for setor in time.get("initialLineup", []):
                for jogador in setor:
                    adicionar_jogador(
                        jogadores=jogadores,
                        jogador=jogador,
                        time=time,
                        match_id=match_id,
                        rodada=rodada,
                        tipo_escalacao="titular"
                    )

            # substitutes é uma lista simples
            for jogador in time.get("substitutes", []):
                adicionar_jogador(
                    jogadores=jogadores,
                    jogador=jogador,
                    time=time,
                    match_id=match_id,
                    rodada=rodada,
                    tipo_escalacao="reserva"
                )

    salvar_json(
        ARQUIVO_JOGADORES,
        list(jogadores.values())
    )

    return jogadores


def mostrar_resumo(jogadores):
    """
    Exibe um resumo do cadastro.
    """

    print(
        f"\nTotal de jogadores cadastrados: "
        f"{len(jogadores)}"
    )

    print("\nPrimeiros jogadores:")

    for jogador in list(jogadores.values())[:10]:
        print(
            f'{jogador["id"]} | '
            f'{jogador["nome"]} | '
            f'{jogador["posicao"]} | '
            f'{jogador["time"]["nome"]}'
        )


if __name__ == "__main__":
    # Carrega as partidas do JSON ou consulta a API
    partidas = carregar_ou_buscar_partidas()

    print(
        f"\nPartidas disponíveis: "
        f"{len(partidas)}"
    )

    # Seleciona três rodadas completas já disputadas
    partidas_selecionadas = selecionar_tres_rodadas(
        partidas
    )

    print(
        f"Partidas selecionadas: "
        f"{len(partidas_selecionadas)}"
    )

    # Busca ou reutiliza as escalações
    lineups = buscar_lineups(
        partidas_selecionadas
    )

    # Monta o cadastro sem fazer novas consultas
    jogadores = extrair_jogadores(lineups)

    mostrar_resumo(jogadores)

    print(
        f"\nCadastro salvo em:"
        f"\n{ARQUIVO_JOGADORES}"
    )