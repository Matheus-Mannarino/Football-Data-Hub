import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

URL_BOX_SCORE = (
    "https://soccer.highlightly.net/box-score"
)

HEADERS = {
    "x-rapidapi-key": API_KEY
}

PASTA_DADOS = Path(__file__).parent / "dados"

PASTA_BOX_SCORES = (
    PASTA_DADOS / "box_scores_2026"
)

ARQUIVO_PARTIDAS = (
    PASTA_DADOS / "partidas_2026.json"
)

ARQUIVO_CONTROLE = (
    PASTA_DADOS / "controle_box_scores_2026.json"
)

# Primeiro teste com 5 partidas.
# Após validar o cache, altere para 80.
MAX_REQUISICOES_POR_EXECUCAO = 75


def carregar_json(caminho, valor_padrao):
    """
    Carrega um arquivo JSON.

    Caso o arquivo não exista, retorna o valor padrão.
    """

    if not caminho.exists():
        return valor_padrao

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    """
    Salva dados em formato JSON.
    """

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def converter_data(data_texto):
    """
    Converte a data da API para datetime.
    """

    if not data_texto:
        return None

    try:
        return datetime.fromisoformat(
            data_texto.replace(
                "Z",
                "+00:00"
            )
        )

    except ValueError:
        return None


def obter_descricao_estado(partida):
    """
    Obtém a descrição do estado da partida.
    """

    estado = partida.get("state", {})

    return str(
        estado.get("description", "")
    ).lower().strip()


def partida_esta_concluida(partida):
    """
    Verifica se uma partida já foi concluída.

    Primeiro verifica a data e depois o estado
    informado pela API.
    """

    data = converter_data(
        partida.get("date")
    )

    if data is None:
        return False

    agora = datetime.now(timezone.utc)

    # Impede a consulta de partidas futuras
    if data > agora:
        return False

    descricao = obter_descricao_estado(
        partida
    )

    estados_concluidos = {
        "finished",
        "full time",
        "after extra time",
        "after penalties",
        "ended"
    }

    if descricao in estados_concluidos:
        return True

    # Aceita descrições maiores que contenham
    # termos comuns de encerramento
    termos_encerramento = [
        "finished",
        "full time",
        "after penalties",
        "after extra time"
    ]

    return any(
        termo in descricao
        for termo in termos_encerramento
    )


def listar_estados_encontrados(partidas):
    """
    Mostra todos os estados encontrados no JSON.
    Isso ajuda a validar o filtro de partidas concluídas.
    """

    estados = set()

    for partida in partidas:
        descricao = obter_descricao_estado(
            partida
        )

        if descricao:
            estados.add(descricao)

    print("\nEstados encontrados nas partidas:")

    for estado in sorted(estados):
        print(f"- {estado}")


def caminho_box_score(match_id):
    """
    Retorna o caminho do JSON de uma partida.
    """

    return (
        PASTA_BOX_SCORES
        / f"{match_id}.json"
    )


def consultar_box_score(match_id):
    """
    Consulta o box score de uma partida.
    """

    url = (
        f"{URL_BOX_SCORE}/"
        f"{match_id}"
    )

    try:
        return requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    except requests.RequestException as erro:
        print(
            f"Erro de conexão na partida "
            f"{match_id}: {erro}"
        )

        return None


def contar_jogadores(box_score):
    """
    Conta quantos jogadores aparecem na resposta.
    """

    if not isinstance(box_score, list):
        return 0

    total = 0

    for registro_time in box_score:
        total += len(
            registro_time.get(
                "players",
                []
            )
        )

    return total


def registrar_controle(
    controle,
    partida,
    status,
    quantidade_jogadores=0,
    status_http=None
):
    """
    Registra o resultado do processamento
    de uma partida.
    """

    match_id = str(partida.get("id"))

    controle[match_id] = {
        "matchId": partida.get("id"),
        "round": partida.get("round"),
        "date": partida.get("date"),
        "homeTeam": partida.get(
            "homeTeam",
            {}
        ).get("name"),
        "awayTeam": partida.get(
            "awayTeam",
            {}
        ).get("name"),
        "status": status,
        "statusHttp": status_http,
        "quantidadeJogadores": quantidade_jogadores,
        "processadoEm": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    salvar_json(
        ARQUIVO_CONTROLE,
        controle
    )


def box_score_ja_processado(
    partida,
    controle
):
    """
    Verifica se a partida já foi processada.
    """

    match_id = partida.get("id")
    match_id_texto = str(match_id)

    # Se o JSON já existe, não consulta novamente
    if caminho_box_score(match_id).exists():
        return True

    # Também ignora partidas já registradas
    # como sem dados
    if match_id_texto in controle:
        status = controle[
            match_id_texto
        ].get("status")

        if status in {
            "coletado",
            "sem_dados",
            "nao_encontrado"
        }:
            return True

    return False


def selecionar_partidas_pendentes(
    partidas,
    controle
):
    """
    Seleciona partidas concluídas que ainda
    não possuem box score salvo.
    """

    concluidas = [
        partida
        for partida in partidas
        if partida_esta_concluida(partida)
    ]

    concluidas.sort(
        key=lambda partida: partida.get(
            "date",
            ""
        )
    )

    pendentes = [
        partida
        for partida in concluidas
        if not box_score_ja_processado(
            partida,
            controle
        )
    ]

    return concluidas, pendentes


def coletar_box_scores():
    """
    Coleta os box scores das partidas concluídas
    respeitando o limite por execução.
    """

    if not API_KEY:
        print(
            "API_KEY não encontrada no arquivo .env."
        )

        return

    partidas = carregar_json(
        ARQUIVO_PARTIDAS,
        []
    )

    if not partidas:
        print(
            "Nenhuma partida foi encontrada em "
            "partidas_2026.json."
        )

        return

    controle = carregar_json(
        ARQUIVO_CONTROLE,
        {}
    )

    PASTA_BOX_SCORES.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 60)
    print("COLETA DE BOX SCORES — BRASILEIRÃO 2026")
    print("=" * 60)

    print(
        f"\nTotal de partidas cadastradas: "
        f"{len(partidas)}"
    )

    listar_estados_encontrados(
        partidas
    )

    concluidas, pendentes = (
        selecionar_partidas_pendentes(
            partidas,
            controle
        )
    )

    print(
        f"\nPartidas concluídas: "
        f"{len(concluidas)}"
    )

    print(
        f"Partidas pendentes: "
        f"{len(pendentes)}"
    )

    if not concluidas:
        print(
            "\nNenhuma partida concluída foi identificada."
        )

        print(
            "Confira os estados apresentados acima."
        )

        return

    if not pendentes:
        print(
            "\nTodas as partidas concluídas "
            "já foram processadas."
        )

        return

    requisicoes = 0
    coletadas = 0
    sem_dados = 0
    erros_temporarios = 0

    for partida in pendentes:
        if (
            requisicoes
            >= MAX_REQUISICOES_POR_EXECUCAO
        ):
            print(
                "\nLimite definido para esta "
                "execução atingido."
            )

            break

        match_id = partida.get("id")

        time_casa = partida.get(
            "homeTeam",
            {}
        ).get(
            "name",
            "Time desconhecido"
        )

        time_fora = partida.get(
            "awayTeam",
            {}
        ).get(
            "name",
            "Time desconhecido"
        )

        print("\n" + "-" * 60)

        print(
            f"Consultando "
            f"{requisicoes + 1}/"
            f"{MAX_REQUISICOES_POR_EXECUCAO}"
        )

        print(
            f"Rodada: "
            f'{partida.get("round")}'
        )

        print(
            f"Partida: "
            f"{time_casa} x {time_fora}"
        )

        print(
            f"Match ID: {match_id}"
        )

        response = consultar_box_score(
            match_id
        )

        if response is None:
            erros_temporarios += 1

            # Não marca como processada para permitir
            # nova tentativa no futuro
            continue

        requisicoes += 1

        print(
            f"Status HTTP: "
            f"{response.status_code}"
        )

        if response.status_code == 429:
            print(
                "\nLimite diário da API atingido."
            )

            print(
                "O progresso anterior está salvo."
            )

            break

        if response.status_code == 404:
            print(
                "Box score não encontrado."
            )

            registrar_controle(
                controle=controle,
                partida=partida,
                status="nao_encontrado",
                status_http=404
            )

            sem_dados += 1

            continue

        if response.status_code >= 500:
            print(
                "Erro temporário no servidor."
            )

            print(
                "A partida será tentada novamente."
            )

            erros_temporarios += 1

            continue

        if response.status_code != 200:
            print(
                "Não foi possível obter o box score."
            )

            print(response.text)

            # Não registra para permitir nova tentativa
            continue

        try:
            box_score = response.json()

        except requests.exceptions.JSONDecodeError:
            print(
                "A API não retornou um JSON válido."
            )

            erros_temporarios += 1

            continue

        quantidade_jogadores = contar_jogadores(
            box_score
        )

        if quantidade_jogadores == 0:
            print(
                "A resposta não contém jogadores."
            )

            registrar_controle(
                controle=controle,
                partida=partida,
                status="sem_dados",
                quantidade_jogadores=0,
                status_http=200
            )

            sem_dados += 1

            continue

        # Salva o box score da partida
        salvar_json(
            caminho_box_score(match_id),
            box_score
        )

        registrar_controle(
            controle=controle,
            partida=partida,
            status="coletado",
            quantidade_jogadores=(
                quantidade_jogadores
            ),
            status_http=200
        )

        coletadas += 1

        print(
            f"Box score salvo com "
            f"{quantidade_jogadores} jogadores."
        )

        # Pequeno intervalo entre chamadas
        time.sleep(0.3)

    concluidas_atualizadas, pendentes_atualizadas = (
        selecionar_partidas_pendentes(
            partidas,
            controle
        )
    )

    arquivos_salvos = len(
        list(
            PASTA_BOX_SCORES.glob("*.json")
        )
    )

    print("\n" + "=" * 60)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 60)

    print(
        f"Requisições realizadas: "
        f"{requisicoes}"
    )

    print(
        f"Box scores coletados nesta execução: "
        f"{coletadas}"
    )

    print(
        f"Partidas sem dados: "
        f"{sem_dados}"
    )

    print(
        f"Erros temporários: "
        f"{erros_temporarios}"
    )

    print(
        f"Total de arquivos salvos: "
        f"{arquivos_salvos}"
    )

    print(
        f"Partidas concluídas restantes: "
        f"{len(pendentes_atualizadas)}"
    )

    print(
        f"\nPasta dos box scores:"
        f"\n{PASTA_BOX_SCORES}"
    )


if __name__ == "__main__":
    coletar_box_scores()