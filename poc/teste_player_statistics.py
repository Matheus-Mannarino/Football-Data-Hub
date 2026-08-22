import json
import os
import unicodedata
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
    PASTA_DADOS / "estatistica_thiago_mendes.json"
)


def carregar_json(caminho):
    """
    Carrega e retorna o conteúdo de um arquivo JSON.
    """

    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        return None

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    """
    Salva os dados em um arquivo JSON.
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
    Remove acentos e transforma o texto em minúsculo.

    Exemplo:
    'Série A' -> 'serie a'
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


def buscar_jogador_localmente(jogadores, nome_procurado):
    """
    Procura jogadores pelo nome no cadastro local.

    Essa função não consulta a API.
    """

    nome_procurado = normalizar_texto(
        nome_procurado
    )

    encontrados = []

    for jogador in jogadores:
        nome_jogador = normalizar_texto(
            jogador.get("nome", "")
        )

        if nome_procurado in nome_jogador:
            encontrados.append(jogador)

    return encontrados


def mostrar_jogadores_encontrados(jogadores):
    """
    Exibe os jogadores encontrados no cadastro local.
    """

    if not jogadores:
        print("Nenhum jogador foi encontrado.")
        return

    print("\nJogadores encontrados:")

    for numero, jogador in enumerate(
        jogadores,
        start=1
    ):
        time = jogador.get("time", {})

        print(
            f"{numero}. "
            f'ID: {jogador.get("id")} | '
            f'Nome: {jogador.get("nome")} | '
            f'Posição: {jogador.get("posicao")} | '
            f'Time: {time.get("nome")}'
        )


def selecionar_jogador_do_vasco(jogadores):
    """
    Seleciona o jogador associado ao Vasco.
    """

    jogadores_vasco = []

    for jogador in jogadores:
        time = jogador.get("time", {})
        nome_time = normalizar_texto(
            time.get("nome", "")
        )

        if "vasco" in nome_time:
            jogadores_vasco.append(jogador)

    if len(jogadores_vasco) == 1:
        return jogadores_vasco[0]

    if len(jogadores_vasco) == 0:
        print(
            "\nThiago Mendes associado ao Vasco "
            "não foi encontrado."
        )
    else:
        print(
            "\nMais de um Thiago Mendes associado "
            "ao Vasco foi encontrado."
        )

    return None


def buscar_estatisticas(player_id):
    """
    Consulta todas as estatísticas de um jogador.

    Essa função realiza uma requisição à API.
    """

    url = (
        f"{URL_PLAYERS}/"
        f"{player_id}/statistics"
    )

    print(
        f"\nConsultando estatísticas do jogador "
        f"{player_id}..."
    )

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    except requests.RequestException as erro:
        print("Erro de conexão com a API:")
        print(erro)

        return None

    print(
        "Status da requisição:",
        response.status_code
    )

    if response.status_code == 429:
        print("Limite diário da API atingido.")
        return None

    if response.status_code != 200:
        print(
            "Não foi possível obter "
            "as estatísticas."
        )

        print("Resposta da API:")
        print(response.text)

        return None

    return response.json()


def obter_dados_do_jogador(dados):
    """
    Obtém o objeto principal do jogador.

    A API normalmente retorna uma lista contendo
    um objeto.
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
    Retorna somente as estatísticas do Campeonato
    Brasileiro Série A da temporada de 2026.
    """

    jogador = obter_dados_do_jogador(dados)

    if jogador is None:
        return None

    competicoes = jogador.get(
        "perCompetition",
        []
    )

    for estatistica in competicoes:
        nome_competicao = normalizar_texto(
            estatistica.get("league", "")
        )

        temporada = str(
            estatistica.get("season", "")
        )

        clube = normalizar_texto(
            estatistica.get("club", "")
        )

        brasileirao = (
            "campeonato brasileiro serie a"
            in nome_competicao
        )

        temporada_correta = (
            temporada == "2026"
        )

        jogador_do_vasco = (
            "vasco" in clube
        )

        if (
            brasileirao
            and temporada_correta
            and jogador_do_vasco
        ):
            return estatistica

    return None


def montar_dados_filtrados(
    jogador_local,
    dados_api,
    estatistica
):
    """
    Organiza somente os dados necessários
    do jogador e do Brasileirão 2026.
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
            )
        },
        "competicao": estatistica
    }


def mostrar_estatisticas_brasileirao(dados):
    """
    Exibe somente as estatísticas do Brasileirão 2026.
    """

    jogador = dados["jogador"]
    estatistica = dados["competicao"]

    print("\nDADOS DO JOGADOR")

    print("ID:", jogador.get("id"))
    print("Nome:", jogador.get("nome"))
    print(
        "Nome completo:",
        jogador.get("nomeCompleto")
    )
    print("Posição:", jogador.get("posicao"))

    print("\nESTATÍSTICAS DO BRASILEIRÃO 2026")
    print("-" * 50)

    print("Clube:", estatistica.get("club"))
    print(
        "Competição:",
        estatistica.get("league")
    )
    print(
        "Temporada:",
        estatistica.get("season")
    )
    print("Tipo:", estatistica.get("type"))
    print(
        "Partidas:",
        estatistica.get("gamesPlayed")
    )
    print(
        "Minutos:",
        estatistica.get("minutesPlayed")
    )
    print("Gols:", estatistica.get("goals"))
    print(
        "Assistências:",
        estatistica.get("assists")
    )
    print(
        "Gols contra:",
        estatistica.get("ownGoals")
    )
    print(
        "Cartões amarelos:",
        estatistica.get("yellowCards")
    )
    print(
        "Cartões vermelhos:",
        estatistica.get("redCards")
    )
    print(
        "Segundo cartão amarelo:",
        estatistica.get(
            "secondYellowCards"
        )
    )
    print(
        "Entrou como reserva:",
        estatistica.get("substitutedIn")
    )
    print(
        "Foi substituído:",
        estatistica.get("substitutedOut")
    )
    print(
        "Pênaltis marcados:",
        estatistica.get("penaltiesScored")
    )


if __name__ == "__main__":
    # 1. Carrega os 666 jogadores cadastrados
    jogadores = carregar_json(
        ARQUIVO_JOGADORES
    )

    if jogadores is None:
        print(
            "Não foi possível carregar "
            "o cadastro de jogadores."
        )

    else:
        # 2. Procura Thiago Mendes no JSON local
        encontrados = buscar_jogador_localmente(
            jogadores,
            "Thiago Mendes"
        )

        mostrar_jogadores_encontrados(
            encontrados
        )

        # 3. Seleciona Thiago Mendes do Vasco
        thiago_mendes = selecionar_jogador_do_vasco(
            encontrados
        )

        if thiago_mendes is not None:
            print("\nJogador selecionado:")

            print(
                "Nome:",
                thiago_mendes.get("nome")
            )

            print(
                "ID:",
                thiago_mendes.get("id")
            )

            print(
                "Time:",
                thiago_mendes.get(
                    "time",
                    {}
                ).get("nome")
            )

            # 4. Faz uma única requisição
            estatisticas_completas = (
                buscar_estatisticas(
                    thiago_mendes["id"]
                )
            )

            if estatisticas_completas is not None:
                # 5. Filtra somente o Brasileirão 2026
                brasileirao_2026 = (
                    filtrar_brasileirao_2026(
                        estatisticas_completas
                    )
                )

                if brasileirao_2026 is None:
                    print(
                        "\nNão foram encontradas "
                        "estatísticas do Brasileirão "
                        "2026 para Thiago Mendes."
                    )

                else:
                    # 6. Organiza os dados filtrados
                    dados_filtrados = (
                        montar_dados_filtrados(
                            jogador_local=thiago_mendes,
                            dados_api=(
                                estatisticas_completas
                            ),
                            estatistica=brasileirao_2026
                        )
                    )

                    # 7. Salva somente o recorte desejado
                    salvar_json(
                        ARQUIVO_ESTATISTICAS,
                        dados_filtrados
                    )

                    # 8. Exibe o resultado
                    mostrar_estatisticas_brasileirao(
                        dados_filtrados
                    )

                    print(
                        "\nEstatísticas salvas em:"
                        f"\n{ARQUIVO_ESTATISTICAS}"
                    )