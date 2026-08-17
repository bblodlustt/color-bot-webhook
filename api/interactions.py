"""
Endpoint de "Interactions" de Discord para el bot de colores.
Este archivo se despliega en Vercel como función serverless (ruta: /api/interactions).
No necesita estar corriendo 24/7 -- Vercel lo "despierta" solo cuando alguien usa un comando.
"""

import io
import json
import os

from flask import Flask, request, Response, abort
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from PIL import Image, ImageDraw, ImageFont
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = Flask(__name__)

PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]

# ---------------------------------------------------------------------------
# Paleta de colores organizada por categoría
# ---------------------------------------------------------------------------
PALETTE = {
    "browns": {
        "thorns": "#594336",
        "chocolate": "#694D42",
        "honey bear": "#81594B",
        "pooh bear": "#705857",
        "choco milk": "#A07E75",
        "honey pot": "#DFA278",
    },
    "oranges": {
        "peach": "#FC8768",
        "tangerine": "#FAB883",
        "carmal latte": "#D08163",
        "bagel": "#E88136",
        "orange": "#CB6204",
        "pumpkin spice": "#A0501C",
    },
    "yellows": {
        "pina colada": "#F7F8C7",
        "sugar cookie": "#EFDC85",
        "banana milk": "#FBFA82",
        "lemon": "#EBF903",
        "banana": "#E8CA20",
        "honey": "#CBAA2F",
    },
    "greens": {
        "matcha": "#9EBAA4",
        "lime": "#A6F8AE",
        "leaf": "#2ABE5F",
        "vine": "#139B30",
        "wasabi": "#3F7C4B",
        "lotus": "#5AB998",
    },
    "blues": {
        "angel milk": "#C6EBFB",
        "snowflake": "#99D3FB",
        "sherbet": "#74EDFA",
        "diamond": "#08BBFD",
        "blueberry muffin": "#6F90D8",
        "whale": "#0350FA",
    },
    "purples": {
        "octopus": "#CAB8FB",
        "solar": "#A688EF",
        "candyfloss": "#986CBD",
        "purple macaroon": "#B354F1",
        "grape": "#814B99",
        "grape jelly": "#6A4182",
    },
    "pinks": {
        "cherry blossom": "#EFADCA",
        "cake": "#F599E5",
        "mochi": "#DE7A9D",
        "ice cream": "#F66CF7",
        "blossom": "#FC30E7",
        "cupcake icing": "#D63D6F",
    },
    "reds": {
        "strawberry milk": "#EC9796",
        "cherry": "#C95560",
        "iced raspberry latte": "#EF463C",
        "strawberry": "#C8353E",
        "apple": "#FB0105",
        "red velvet cake": "#651021",
    },
    "neutrals": {
        "black": "#000000",
        "cool grey": "#5A5668",
        "grey": "#514E58",
        "warm grey": "#897A7D",
        "ivory": "#E4DBCF",
        "white": "#FAFBFD",
    },
}

FLAT = {
    name: (cat, hexcode)
    for cat, colors in PALETTE.items()
    for name, hexcode in colors.items()
}


def hex_to_int(hexcode: str) -> int:
    return int(hexcode.lstrip("#"), 16)


def hex_to_rgb(hexcode: str):
    h = hexcode.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def generar_imagen_categoria(categoria: str) -> bytes:
    colores = PALETTE[categoria]
    columnas = 3
    filas = (len(colores) + columnas - 1) // columnas

    celda_w, celda_h = 220, 130
    padding = 16
    ancho = columnas * celda_w + padding * 2
    alto = filas * celda_h + padding * 2

    img = Image.new("RGB", (ancho, alto), (35, 35, 40))
    draw = ImageDraw.Draw(img)

    try:
        fuente_nombre = ImageFont.truetype("arial.ttf", 18)
        fuente_hex = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        fuente_nombre = ImageFont.load_default()
        fuente_hex = ImageFont.load_default()

    for i, (nombre, hexcode) in enumerate(colores.items()):
        col = i % columnas
        fila = i // columnas
        x0 = padding + col * celda_w
        y0 = padding + fila * celda_h

        rgb = hex_to_rgb(hexcode)
        swatch_size = 90
        swatch_box = [x0 + 10, y0 + 10, x0 + 10 + swatch_size, y0 + 10 + swatch_size]
        draw.rounded_rectangle(swatch_box, radius=14, fill=rgb, outline=(70, 70, 75), width=2)

        texto_x = x0 + 10
        texto_y = y0 + 10 + swatch_size + 6
        draw.text((texto_x, texto_y), nombre.title(), font=fuente_nombre, fill=(230, 230, 230))
        draw.text((texto_x, texto_y + 20), hexcode, font=fuente_hex, fill=(160, 160, 165))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def verificar_firma(req) -> bool:
    firma = req.headers.get("X-Signature-Ed25519", "")
    timestamp = req.headers.get("X-Signature-Timestamp", "")
    cuerpo = req.data.decode("utf-8")
    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{cuerpo}".encode(), bytes.fromhex(firma))
        return True
    except (BadSignatureError, ValueError, Exception):
        return False


def obtener_opciones(data: dict) -> dict:
    opciones = data.get("data", {}).get("options", [])
    return {opt["name"]: opt["value"] for opt in opciones}


@app.route("/api/interactions", methods=["POST"])
def interactions():
    if not verificar_firma(request):
        abort(401, "invalid request signature")

    data = request.json

    # PING de verificación de Discord
    if data["type"] == 1:
        return jsonify_simple({"type": 1})

    if data["type"] == 2:  # es un comando
        nombre_comando = data["data"]["name"]
        opciones = obtener_opciones(data)

        if nombre_comando == "color":
            return manejar_color(opciones)
        if nombre_comando == "colors":
            return manejar_colors(opciones)
        if nombre_comando == "categories":
            return manejar_categories()

    return jsonify_simple({"type": 4, "data": {"content": "Comando no reconocido."}})


def jsonify_simple(payload: dict):
    return Response(json.dumps(payload), mimetype="application/json")


def manejar_color(opciones: dict):
    nombre = opciones.get("nombre", "").strip().lower()
    if nombre not in FLAT:
        return jsonify_simple(
            {
                "type": 4,
                "data": {
                    "content": f"No encontré '{nombre}'. Usa /categories o /colors para ver las opciones.",
                    "flags": 64,  # respuesta solo visible para quien lo escribió
                },
            }
        )

    categoria, hexcode = FLAT[nombre]
    embed = {
        "title": nombre.title(),
        "description": f"Categoría: **{categoria.title()}**\nHex: `{hexcode}`",
        "color": hex_to_int(hexcode),
    }
    return jsonify_simple({"type": 4, "data": {"embeds": [embed]}})


def manejar_colors(opciones: dict):
    categoria = opciones.get("categoria", "").strip().lower()
    if categoria not in PALETTE:
        return jsonify_simple(
            {
                "type": 4,
                "data": {
                    "content": f"No encontré la categoría '{categoria}'. Usa /categories para ver las disponibles.",
                    "flags": 64,
                },
            }
        )

    primer_hex = next(iter(PALETTE[categoria].values()))
    imagen_bytes = generar_imagen_categoria(categoria)

    embed = {"title": categoria.title(), "color": hex_to_int(primer_hex), "image": {"url": "attachment://paleta.png"}}
    payload = {"type": 4, "data": {"embeds": [embed]}}

    mp_encoder = MultipartEncoder(
        fields={
            "payload_json": (None, json.dumps(payload), "application/json"),
            "files[0]": ("paleta.png", imagen_bytes, "image/png"),
        }
    )
    return Response(mp_encoder.to_string(), mimetype=mp_encoder.content_type)


def manejar_categories():
    lista = ", ".join(c.title() for c in PALETTE.keys())
    return jsonify_simple({"type": 4, "data": {"content": f"Categorías disponibles: {lista}"}})
