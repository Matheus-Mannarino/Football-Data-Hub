import json
from pathlib import Path
from collections import Counter

pasta_box_scores = Path(__file__).parent / "dados" / "box_scores_2026"

arquivos_json = list(pasta_box_scores.glob("*.json"))

print(f"Pasta analisada: {pasta_box_scores}")
print(f"Quantidade de arquivos JSON: {len(arquivos_json)}")

arquivos_validos = 0
arquivos_com_erro = []
estruturas_invalidas = []
total_equipes = 0
total_desempenhos = 0

for arquivo in arquivos_json:
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, list) or len(dados) != 2:
            estruturas_invalidas.append(
                f"{arquivo.name}: esperado lista com 2 equipes"
            )
            continue

        estrutura_valida = True

        for equipe in dados:
            if not isinstance(equipe, dict):
                estrutura_valida = False
                break

            if "team" not in equipe or "players" not in equipe:
                estrutura_valida = False
                break

            if not isinstance(equipe["players"], list):
                estrutura_valida = False
                break

            total_equipes += 1
            total_desempenhos += len(equipe["players"])

        if estrutura_valida:
            arquivos_validos += 1
        else:
            estruturas_invalidas.append(
                f"{arquivo.name}: estrutura de equipe inválida"
            )

    except (json.JSONDecodeError, OSError) as erro:
        arquivos_com_erro.append(f"{arquivo.name}: {erro}")

print("\n--- VALIDAÇÃO DA ESTRUTURA ---")
print(f"Arquivos válidos: {arquivos_validos}")
print(f"Arquivos com erro de leitura: {len(arquivos_com_erro)}")
print(f"Arquivos com estrutura inválida: {len(estruturas_invalidas)}")
print(f"Equipes analisadas: {total_equipes}")
print(f"Desempenhos de jogadores encontrados: {total_desempenhos}")

if arquivos_com_erro:
    print("\nErros de leitura:")
    for erro in arquivos_com_erro[:10]:
        print(f"- {erro}")

if estruturas_invalidas:
    print("\nEstruturas inválidas:")
    for erro in estruturas_invalidas[:10]:
        print(f"- {erro}")

jogadores_unicos = set()
jogadores_com_logo = set()
jogadores_sem_logo = set()
registros_sem_id = 0
registros_sem_nome_completo = 0
duplicados_na_partida = []

for arquivo in arquivos_json:
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    jogadores_da_partida = set()

    for equipe in dados:
        for jogador in equipe["players"]:
            jogador_id = jogador.get("id")
            nome_completo = jogador.get("fullName")
            logo = jogador.get("logo")

            if jogador_id is None:
                registros_sem_id += 1
                continue

            jogadores_unicos.add(jogador_id)

            if nome_completo is None or nome_completo.strip() == "":
                registros_sem_nome_completo += 1

            if logo:
                jogadores_com_logo.add(jogador_id)
            else:
                jogadores_sem_logo.add(jogador_id)

            if jogador_id in jogadores_da_partida:
                duplicados_na_partida.append(
                    f"{arquivo.name}: jogador {jogador_id}"
                )
            else:
                jogadores_da_partida.add(jogador_id)

print("\n--- VALIDAÇÃO DOS JOGADORES ---")
print(f"Jogadores únicos: {len(jogadores_unicos)}")
print(f"Jogadores com logo: {len(jogadores_com_logo)}")
print(f"Jogadores sem logo: {len(jogadores_sem_logo)}")
print(f"Registros sem ID: {registros_sem_id}")
print(f"Registros sem nome completo: {registros_sem_nome_completo}")
print(f"Duplicações na mesma partida: {len(duplicados_na_partida)}")

if duplicados_na_partida:
    print("\nExemplos de duplicações:")
    for duplicacao in duplicados_na_partida[:10]:
        print(f"- {duplicacao}")

jogadores_sem_full_name = set()
registros_sem_qualquer_nome = []
nomes_por_jogador = {}

for arquivo in arquivos_json:
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for equipe in dados:
        for jogador in equipe["players"]:
            jogador_id = jogador.get("id")
            nome_curto = jogador.get("name")
            nome_completo = jogador.get("fullName")

            if jogador_id is None:
                continue

            if not nome_completo:
                jogadores_sem_full_name.add(jogador_id)

            nome_escolhido = nome_completo or nome_curto

            if not nome_escolhido:
                registros_sem_qualquer_nome.append(
                    f"{arquivo.name}: jogador {jogador_id}"
                )
                continue

            if jogador_id not in nomes_por_jogador:
                nomes_por_jogador[jogador_id] = set()

            nomes_por_jogador[jogador_id].add(nome_escolhido)

jogadores_com_nomes_diferentes = {
    jogador_id: nomes
    for jogador_id, nomes in nomes_por_jogador.items()
    if len(nomes) > 1
}

print("\n--- VALIDAÇÃO DOS NOMES ---")
print(
    f"Jogadores únicos sem fullName em alguma atuação: "
    f"{len(jogadores_sem_full_name)}"
)
print(
    f"Registros sem fullName e sem name: "
    f"{len(registros_sem_qualquer_nome)}"
)
print(
    f"Jogadores que apareceram com nomes diferentes: "
    f"{len(jogadores_com_nomes_diferentes)}"
)

if jogadores_com_nomes_diferentes:
    print("\nExemplos de nomes diferentes para o mesmo ID:")

    for jogador_id, nomes in list(
        jogadores_com_nomes_diferentes.items()
    )[:10]:
        print(f"- {jogador_id}: {sorted(nomes)}")

inconsistencias = {
    "passes": [],
    "dribles": [],
    "duelos": [],
    "penaltis": [],
    "finalizacoes": []
}

for arquivo in arquivos_json:
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for equipe in dados:
        for jogador in equipe["players"]:
            jogador_id = jogador.get("id")
            estatisticas = jogador.get("statistics", {})

            passes_total = estatisticas.get("passesTotal")
            passes_certos = estatisticas.get("passesSuccessful")
            passes_errados = estatisticas.get("passesFailed")

            if (
                passes_total is not None
                and passes_certos is not None
                and passes_errados is not None
                and passes_total != passes_certos + passes_errados
            ):
                inconsistencias["passes"].append(
                    f"{arquivo.name} | jogador {jogador_id}: "
                    f"{passes_total} != {passes_certos} + {passes_errados}"
                )

            dribles_total = estatisticas.get("dribblesTotal")
            dribles_certos = estatisticas.get("dribblesSuccessful")
            dribles_errados = estatisticas.get("dribblesFailed")

            if (
                dribles_total is not None
                and dribles_certos is not None
                and dribles_errados is not None
                and dribles_total != dribles_certos + dribles_errados
            ):
                inconsistencias["dribles"].append(
                    f"{arquivo.name} | jogador {jogador_id}: "
                    f"{dribles_total} != {dribles_certos} + {dribles_errados}"
                )

            duelos_total = estatisticas.get("duelsTotal")
            duelos_vencidos = estatisticas.get("duelsWon")
            duelos_perdidos = estatisticas.get("duelsLost")

            if (
                duelos_total is not None
                and duelos_vencidos is not None
                and duelos_perdidos is not None
                and duelos_total != duelos_vencidos + duelos_perdidos
            ):
                inconsistencias["duelos"].append(
                    f"{arquivo.name} | jogador {jogador_id}: "
                    f"{duelos_total} != {duelos_vencidos} + {duelos_perdidos}"
                )

            penaltis_total = estatisticas.get("penaltiesTotal")
            penaltis_marcados = estatisticas.get("penaltiesScored")
            penaltis_perdidos = estatisticas.get("penaltiesMissed")

            if (
                penaltis_total is not None
                and penaltis_marcados is not None
                and penaltis_perdidos is not None
                and penaltis_total != penaltis_marcados + penaltis_perdidos
            ):
                inconsistencias["penaltis"].append(
                    f"{arquivo.name} | jogador {jogador_id}: "
                    f"{penaltis_total} != "
                    f"{penaltis_marcados} + {penaltis_perdidos}"
                )

            finalizacoes_total = estatisticas.get("shotsTotal")
            finalizacoes_alvo = estatisticas.get("shotsOnTarget")
            finalizacoes_fora = estatisticas.get("shotsOffTarget")

            if (
                finalizacoes_total is not None
                and finalizacoes_alvo is not None
                and finalizacoes_fora is not None
                and finalizacoes_total
                != finalizacoes_alvo + finalizacoes_fora
            ):
                inconsistencias["finalizacoes"].append(
                    f"{arquivo.name} | jogador {jogador_id}: "
                    f"{finalizacoes_total} != "
                    f"{finalizacoes_alvo} + {finalizacoes_fora}"
                )

print("\n--- VALIDAÇÃO DAS RELAÇÕES MATEMÁTICAS ---")

for categoria, erros in inconsistencias.items():
    print(f"{categoria.capitalize()}: {len(erros)} inconsistências")

    for erro in erros[:5]:
        print(f"  - {erro}")

campos_jogador = [
    "id",
    "name",
    "fullName",
    "logo",
    "matchRating",
    "shirtNumber",
    "position",
    "isCaptain",
    "minutesPlayed",
    "isSubstitute",
    "offsides"
]

campos_estatisticas = [
    "goalsScored",
    "goalsSaved",
    "goalsConceded",
    "assists",
    "dribblesTotal",
    "dribblesSuccessful",
    "fouledByOthers",
    "fouledOthers",
    "tacklesTotal",
    "interceptionsTotal",
    "shotsOnTarget",
    "shotsTotal",
    "penaltiesScored",
    "penaltiesTotal",
    "passesSuccessful",
    "passesTotal",
    "passesKey",
    "cardsRed",
    "cardsYellow",
    "cardsSecondYellow",
    "duelsTotal",
    "duelsWon",
    "expectedAssists",
    "expectedGoals",
    "expectedGoalsOnTarget",
    "expectedGoalsOnTargetConceded",
    "expectedGoalsPrevented"
]

ausentes_jogador = Counter()
nulos_jogador = Counter()
ausentes_estatisticas = Counter()
nulos_estatisticas = Counter()
total_registros = 0
sem_objeto_estatisticas = 0

for arquivo in arquivos_json:
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for equipe in dados:
        for jogador in equipe["players"]:
            total_registros += 1

            for campo in campos_jogador:
                if campo not in jogador:
                    ausentes_jogador[campo] += 1
                elif jogador[campo] is None:
                    nulos_jogador[campo] += 1

            estatisticas = jogador.get("statistics")

            if not isinstance(estatisticas, dict):
                sem_objeto_estatisticas += 1
                continue

            for campo in campos_estatisticas:
                if campo not in estatisticas:
                    ausentes_estatisticas[campo] += 1
                elif estatisticas[campo] is None:
                    nulos_estatisticas[campo] += 1

print("\n--- CAMPOS AUSENTES OU NULOS ---")
print(f"Registros analisados: {total_registros}")
print(f"Sem objeto statistics: {sem_objeto_estatisticas}")

print("\nCampos principais:")
for campo in campos_jogador:
    ausentes = ausentes_jogador[campo]
    nulos = nulos_jogador[campo]

    if ausentes > 0 or nulos > 0:
        print(f"- {campo}: {ausentes} ausentes, {nulos} nulos")

print("\nCampos de estatísticas:")
for campo in campos_estatisticas:
    ausentes = ausentes_estatisticas[campo]
    nulos = nulos_estatisticas[campo]

    if ausentes > 0 or nulos > 0:
        print(f"- {campo}: {ausentes} ausentes, {nulos} nulos")

nota_nula_minutos_zero = 0
nota_nula_minutos_positivos = 0
minutos_zero = 0
minutos_zero_titular = 0
minutos_zero_reserva = 0
exemplos_nota_nula_com_minutos = []

for arquivo in arquivos_json:
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    for equipe in dados:
        for jogador in equipe["players"]:
            nota = jogador.get("matchRating")
            minutos = jogador.get("minutesPlayed")
            reserva = jogador.get("isSubstitute")

            if minutos == 0:
                minutos_zero += 1

                if reserva:
                    minutos_zero_reserva += 1
                else:
                    minutos_zero_titular += 1

            if nota is None:
                if minutos == 0:
                    nota_nula_minutos_zero += 1
                elif minutos is not None and minutos > 0:
                    nota_nula_minutos_positivos += 1
                    exemplos_nota_nula_com_minutos.append(
                        f"{arquivo.name}: "
                        f"{jogador.get('fullName') or jogador.get('name')} "
                        f"({minutos} minutos)"
                    )

print("\n--- PARTICIPAÇÃO NA PARTIDA ---")
print(f"Registros com 0 minutos: {minutos_zero}")
print(f"0 minutos e marcado como reserva: {minutos_zero_reserva}")
print(f"0 minutos e marcado como titular: {minutos_zero_titular}")
print(f"Nota nula com 0 minutos: {nota_nula_minutos_zero}")
print(f"Nota nula com minutos positivos: {nota_nula_minutos_positivos}")

if exemplos_nota_nula_com_minutos:
    print("\nExemplos de nota nula com participação:")

    for exemplo in exemplos_nota_nula_com_minutos[:10]:
        print(f"- {exemplo}")