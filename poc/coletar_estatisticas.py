import json
import os
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

URL_PLAYERS = "https://soccer.highlightly.net/players"

HEADERS = {
    "x-rapidapi-key": API_KEY
}

PASTA_DADOS = Path(__file__).parent / "dados"

ARQUIVO_JOGADORES = (
    PASTA_DADOS / "jogadores_2026.json"
)

ARQUIVO_ESTATISTICAS = (
    PASTA_DADOS / "estatisticas_jogadores_2026.json"
)

ARQUIVO_PROCESSADOS = (
    PASTA_DADOS / "jogadores_processados_2026.json"
)

# Primeiro teste com somente 2 jogadores.
# Após validar, altere para 80.
MAX_REQUISICOES_POR_EXECUCAO = 2


def carregar_json(caminho, valor_padrao):
    """
    Carrega um arquivo JSON.

    Caso o arquivo ainda não exista, retorna
    o valor padrão informado.
    """

    if not caminho.exists():
        return valor_padrao

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    """
    Salva dados em um arquivo JSON.
    """

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def normalizar_texto(texto):
    """
    Remove acentos e converte o texto para minúsculo.

    Exemplo:
    'Campeonato Brasileiro Série A'
    passa a ser
    'campeonato brasileiro serie a'
    """

    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    texto_normalizado = unicodedata.normalize(
        "NFD",
        texto
    )

    return "".join(
        caractere
        for caractere in texto_normalizado
        if unicodedata.category(caractere) != "Mn"
    )


def obter_dados_do_jogador(dados):
    """
    Extrai o objeto principal da resposta da API.

    A API normalmente retorna uma lista contendo
    um objeto com os dados do jogador.
    """

    if not dados:
        return None

    if isinstance(dados, list):
        if not dados:
            return None

        return dados[0]

    if isinstance(dados, dict):
        return dados

    return None


def filtrar_brasileirao_2026(dados):
    """
    Retorna uma lista com os registros do jogador
    no Campeonato Brasileiro Série A de 2026.

    O resultado é uma lista porque um jogador pode
    ter defendido dois clubes na mesma temporada.
    """

    jogador_api = obter_dados_do_jogador(dados)

    if jogador_api is None:
        return []

    competicoes = jogador_api.get(
        "perCompetition",
        []
    )

    resultados = []

    for estatistica in competicoes:
        nome_competicao = normalizar_texto(
            estatistica.get("league", "")
        )

        temporada = str(
            estatistica.get("season", "")
        )

        brasileirao = (
            "campeonato brasileiro serie a"
            in nome_competicao
        )

        temporada_correta = (
            temporada == "2026"
        )

        if brasileirao and temporada_correta:
            resultados.append(estatistica)

    return resultados


def consultar_estatisticas(player_id):
    """
    Consulta as estatísticas de um jogador.

    Retorna:
    - resposta HTTP, se a API respondeu;
    - None, se ocorreu erro de conexão.
    """

    url = (
        f"{URL_PLAYERS}/"
        f"{player_id}/statistics"
    )

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        return response

    except requests.RequestException as erro:
        print(
            f"Erro de conexão para o jogador "
            f"{player_id}: {erro}"
        )

        return None


def criar_registro_estatistico(
    jogador_local,
    dados_api,
    competicoes
):
    """
    Organiza os dados que serão salvos.
    """

    jogador_api = obter_dados_do_jogador(
        dados_api
    )

    return {
        "jogador": {
            "id": jogador_local.get("id"),
            "nome": jogador_local.get("nome"),
            "nomeCompleto": jogador_api.get(
                "fullName"
            ),
            "posicao": jogador_local.get(
                "posicao"
            ),
            "timeCadastro": jogador_local.get(
                "time"
            )
        },
        "competicoes": competicoes,
        "consultadoEm": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def registrar_processamento(
    processados,
    jogador,
    status
):
    """
    Registra que determinado jogador já foi consultado.
    """

    jogador_id = str(jogador.get("id"))

    processados[jogador_id] = {
        "id": jogador.get("id"),
        "nome": jogador.get("nome"),
        "time": jogador.get("time"),
        "status": status,
        "processadoEm": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def salvar_progresso(
    estatisticas,
    processados
):
    """
    Salva os dois arquivos após cada jogador.
    """

    salvar_json(
        ARQUIVO_ESTATISTICAS,
        estatisticas
    )

    salvar_json(
        ARQUIVO_PROCESSADOS,
        processados
    )


def coletar_estatisticas():
    """
    Processa jogadores ainda não consultados,
    respeitando o limite definido por execução.
    """

    jogadores = carregar_json(
        ARQUIVO_JOGADORES,
        []
    )

    estatisticas = carregar_json(
        ARQUIVO_ESTATISTICAS,
        {}
    )

    processados = carregar_json(
        ARQUIVO_PROCESSADOS,
        {}
    )

    if not jogadores:
        print(
            "Nenhum jogador foi encontrado em "
            "jogadores_2026.json."
        )

        return

    print("=" * 60)
    print("COLETA DE ESTATÍSTICAS DO BRASILEIRÃO 2026")
    print("=" * 60)

    print(
        f"\nJogadores cadastrados: "
        f"{len(jogadores)}"
    )

    print(
        f"Jogadores já processados: "
        f"{len(processados)}"
    )

    jogadores_pendentes = [
        jogador
        for jogador in jogadores
        if str(jogador.get("id")) not in processados
    ]

    print(
        f"Jogadores pendentes: "
        f"{len(jogadores_pendentes)}"
    )

    if not jogadores_pendentes:
        print(
            "\nTodos os jogadores já foram processados."
        )

        return

    requisicoes_realizadas = 0
    encontrados_brasileirao = 0
    sem_estatisticas = 0
    erros_temporarios = 0

    for jogador in jogadores_pendentes:
        if (
            requisicoes_realizadas
            >= MAX_REQUISICOES_POR_EXECUCAO
        ):
            print(
                "\nLimite definido para esta execução "
                "foi atingido."
            )

            break

        jogador_id = jogador.get("id")
        nome = jogador.get("nome")

        print(
            f"\nConsultando "
            f"{requisicoes_realizadas + 1}/"
            f"{MAX_REQUISICOES_POR_EXECUCAO}"
        )

        print(
            f"Jogador: {nome} | "
            f"ID: {jogador_id}"
        )

        response = consultar_estatisticas(
            jogador_id
        )

        if response is None:
            erros_temporarios += 1

            # Não registra como processado.
            # Será tentado novamente no futuro.
            continue

        requisicoes_realizadas += 1

        print(
            f"Status: {response.status_code}"
        )

        if response.status_code == 429:
            print(
                "\nLimite diário da API atingido."
            )

            print(
                "O progresso obtido até aqui "
                "está salvo."
            )

            break

        if response.status_code == 404:
            print(
                "Jogador não encontrado no endpoint "
                "de estatísticas."
            )

            registrar_processamento(
                processados,
                jogador,
                "jogador_nao_encontrado"
            )

            salvar_progresso(
                estatisticas,
                processados
            )

            continue

        if response.status_code >= 500:
            print(
                "Erro temporário no servidor da API."
            )

            print(
                "O jogador será tentado novamente "
                "em outra execução."
            )

            erros_temporarios += 1

            continue

        if response.status_code != 200:
            print(
                "Não foi possível consultar "
                "este jogador."
            )

            print(response.text)

            # Erros diferentes de 200 não são marcados
            # como concluídos, permitindo nova tentativa.
            continue

        dados_api = response.json()

        competicoes = filtrar_brasileirao_2026(
            dados_api
        )

        jogador_id_texto = str(jogador_id)

        if competicoes:
            registro = criar_registro_estatistico(
                jogador_local=jogador,
                dados_api=dados_api,
                competicoes=competicoes
            )

            estatisticas[jogador_id_texto] = registro

            registrar_processamento(
                processados,
                jogador,
                "estatisticas_encontradas"
            )

            encontrados_brasileirao += 1

            print(
                "Estatísticas do Brasileirão "
                "2026 encontradas."
            )

        else:
            registrar_processamento(
                processados,
                jogador,
                "sem_estatisticas_brasileirao_2026"
            )

            sem_estatisticas += 1

            print(
                "O jogador não possui estatísticas "
                "do Brasileirão 2026."
            )

        # Salva imediatamente após cada jogador
        salvar_progresso(
            estatisticas,
            processados
        )

        # Pequeno intervalo entre chamadas
        time.sleep(0.3)

    jogadores_restantes = (
        len(jogadores)
        - len(processados)
    )

    print("\n" + "=" * 60)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 60)

    print(
        f"Requisições realizadas: "
        f"{requisicoes_realizadas}"
    )

    print(
        f"Estatísticas encontradas nesta execução: "
        f"{encontrados_brasileirao}"
    )

    print(
        f"Sem estatísticas nesta execução: "
        f"{sem_estatisticas}"
    )

    print(
        f"Erros temporários: "
        f"{erros_temporarios}"
    )

    print(
        f"Total de jogadores processados: "
        f"{len(processados)}"
    )

    print(
        f"Jogadores restantes: "
        f"{jogadores_restantes}"
    )

    print(
        f"\nEstatísticas salvas em:"
        f"\n{ARQUIVO_ESTATISTICAS}"
    )

    print(
        f"\nControle salvo em:"
        f"\n{ARQUIVO_PROCESSADOS}"
    )


if __name__ == "__main__":
    coletar_estatisticas()