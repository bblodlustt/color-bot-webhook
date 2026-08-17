from flask import Flask, request, jsonify

app = Flask(__name__)

COLOR_CATEGORIES = {
    "Browns": ["Marrón Claro", "Marrón Oscuro", "Chocolate"],
    "Oranges": ["Naranja", "Coral"],
    "Yellows": ["Amarillo", "Crema"],
    "Greens": ["Verde Lima", "Verde Menta", "Verde Bosque"],
    "Blues": ["Azul Marino", "Azul Cielo", "Turquesa"],
    "Purples": ["Púrpura", "Violeta"],
    "Pinks": ["Rosa Pastel", "Fucsia"]
}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Bot activo"}), 200

@app.route('/', methods=['POST'])
@app.route('/api/interactions', methods=['POST'])
def interactions():
    data = request.get_json(silent=True) or {}
    
    # Responder PING de comprobación de Discord
    if data.get('type') == 1:
        return jsonify({"type": 1})

    # Procesar comandos Slash
    if data.get('type') == 2:
        command_name = data.get('data', {}).get('name')

        if command_name == "colors":
            content = "**Categorías de colores disponibles:**\n\n"
            buttons = []
            count = 1

            for category, color_list in COLOR_CATEGORIES.items():
                content += f"__**{category}**__:\n"
                for color in color_list:
                    content += f"{count}. {color}\n"
                    buttons.append({
                        "type": 2,
                        "style": 1,
                        "label": str(count),
                        "custom_id": f"color_{color.lower().replace(' ', '_')}"
                    })
                    count += 1
                content += "\n"

            components = [
                {"type": 1, "components": buttons[i:i + 5]}
                for i in range(0, len(buttons), 5)
            ]

            return jsonify({
                "type": 4,
                "data": {
                    "content": content.strip(),
                    "components": components
                }
            })

        elif command_name == "categories":
            categories_list = ", ".join(COLOR_CATEGORIES.keys())
            return jsonify({
                "type": 4,
                "data": {"content": f"**Categorías disponibles:** {categories_list}"}
            })

        elif command_name == "color":
            return jsonify({
                "type": 4,
                "data": {"content": "Consulta de color individual recibida."}
            })

    return jsonify({"type": 4, "data": {"content": "Comando no reconocido."}})
