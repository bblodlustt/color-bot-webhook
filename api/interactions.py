# Dentro de la ruta/función que procesa la interacción en Python

colors_data = {
    "Primarios": ["Rojo", "Azul", "Amarillo"],
    "Secundarios": ["Verde", "Naranja", "Morado"]
}

content = "**Lista de colores disponibles**\n\n"
buttons = []
count = 1

for category, color_list in colors_data.items():
    content += f"__{category}__:\n"
    for color in color_list:
        content += f"{count}. {color}\n"
        buttons.append({
            "type": 2,
            "style": 1,
            "label": str(count),
            "custom_id": f"color_{color.lower()}"
        })
        count += 1
    content += "\n"

components = [{"type": 1, "components": buttons[i:i + 5]} for i in range(0, len(buttons), 5)]

return {
    "type": 4,
    "data": {
        "content": content.strip(),
        "components": components
    }
}
