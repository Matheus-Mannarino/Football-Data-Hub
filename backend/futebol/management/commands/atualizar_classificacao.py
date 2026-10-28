import os

import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from futebol.models import Classificacao, Clubes, Temporadas


class Command(BaseCommand):
    help = "Atualiza a classificação do Brasileirão 2026 pela Highlightly."

    def handle(self, *args, **options):
        api_key = os.getenv("API_KEY")

        if not api_key:
            raise CommandError("API_KEY não encontrada no arquivo .env.")

        try:
            temporada = Temporadas.objects.get(
                ano=2026,
                competicao__api_id=61205,
            )
        except Temporadas.DoesNotExist as exc:
            raise CommandError(
                "Temporada do Brasileirão 2026 não encontrada."
            ) from exc

        try:
            response = requests.get(
                "https://soccer.highlightly.net/standings",
                headers={"x-rapidapi-key": api_key},
                params={
                    "leagueId": 61205,
                    "season": 2026,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError(
                "Não foi possível consultar a classificação na API."
            ) from exc

        try:
            dados = response.json()
            standings = dados["groups"][0]["standings"]

            if len(standings) != 20:
                raise ValueError("A resposta deve conter 20 clubes.")

            registros = []

            for item in standings:
                total = item["total"]

                registro = {
                    "api_id": int(item["team"]["id"]),
                    "posicao": int(item["position"]),
                    "pontos": int(item["points"]),
                    "jogos": int(total["games"]),
                    "vitorias": int(total["wins"]),
                    "empates": int(total["draws"]),
                    "derrotas": int(total["loses"]),
                    "gols_pro": int(total["scoredGoals"]),
                    "gols_contra": int(total["receivedGoals"]),
                }

                if any(valor < 0 for valor in registro.values()):
                    raise ValueError("A resposta contém valores negativos.")

                if registro["jogos"] != (
                    registro["vitorias"]
                    + registro["empates"]
                    + registro["derrotas"]
                ):
                    raise ValueError(
                        "Total de jogos diferente de vitórias, empates e derrotas."
                    )

                registros.append(registro)

            api_ids = [registro["api_id"] for registro in registros]
            posicoes = [registro["posicao"] for registro in registros]

            if len(set(api_ids)) != 20:
                raise ValueError("A resposta contém clubes repetidos.")

            if set(posicoes) != set(range(1, 21)):
                raise ValueError("As posições devem ir de 1 a 20, sem repetição.")

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise CommandError(
                f"Resposta da API inválida: {exc}"
            ) from exc

        clubes = {
            clube.api_id: clube
            for clube in Clubes.objects.filter(api_id__in=api_ids)
        }

        ids_ausentes = set(api_ids) - set(clubes)

        if ids_ausentes:
            raise CommandError(
                "Clubes da API não encontrados no banco. IDs: "
                + ", ".join(str(api_id) for api_id in sorted(ids_ausentes))
            )

        atualizado_em = timezone.now()

        with transaction.atomic():
            for registro in registros:
                valores = registro.copy()
                api_id = valores.pop("api_id")

                Classificacao.objects.update_or_create(
                    temporada=temporada,
                    clube=clubes[api_id],
                    defaults={
                        **valores,
                        "atualizado_em": atualizado_em,
                    },
                )

            Classificacao.objects.filter(
                temporada=temporada,
            ).exclude(
                clube_id__in=[clube.id for clube in clubes.values()],
            ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                "Classificação atualizada com sucesso: 20 clubes."
            )
        )