import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

url = "https://soccer.highlightly.net/leagues"

headers = {
    "x-rapidapi-key": API_KEY
}

params = {
    "countryCode": "BR",
    "leagueName": "Serie A",
    "season": 2026
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print("Status:", response.status_code)

dados = response.json()

for liga in dados["data"]:
    print("ID:", liga["id"])
    print("Nome:", liga["name"])
    print("País:", liga["country"]["name"])

    print("Temporadas:")

    for temporada in liga["seasons"]:
        print("-", temporada["season"])
