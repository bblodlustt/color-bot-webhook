"""
Script para registrar los slash commands en Discord.
Se corre UNA SOLA VEZ desde tu computadora (no se sube a Vercel).

Requiere: pip install requests python-dotenv
Necesita un archivo .env en la misma carpeta con:
    DISCORD_APPLICATION_ID=...   (pestaña General Information del Developer Portal)
    DISCORD_TOKEN=...            (pestaña Bot del Developer Portal)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
TOKEN = os.environ["DISCORD_TOKEN"]

URL = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"
HEADERS = {"Authorization": f"Bot {TOKEN}"}

COMMANDS = [
    {
        "name": "color",
        "description": "Muestra el swatch de un color específico",
        "options": [
            {
                "name": "nombre",
                "description": "Nombre del color, por ejemplo 'lemon' o 'honey bear'",
                "type": 3,  # STRING
                "required": True,
            }
        ],
    },
    {
        "name": "colors",
        "description": "Lista todos los colores de una categoría con su swatch",
        "options": [
            {
                "name": "categoria",
                "description": "Categoría, por ejemplo 'yellows' o 'purples'",
                "type": 3,  # STRING
                "required": True,
            }
        ],
    },
    {
        "name": "categories",
        "description": "Lista las categorías de colores disponibles",
    },
]

respuesta = requests.put(URL, headers=HEADERS, json=COMMANDS)
print(respuesta.status_code)
print(respuesta.text)
