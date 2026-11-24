import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Reemplaza estos valores con los de tu app en Meta for Developers
# o pásalos por variables de entorno en tu sistema.
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_de_verificacion")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "TU_ACCESS_TOKEN_AQUI")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "TU_PHONE_NUMBER_ID")


def enviar_mensaje_whatsapp(numero_destino: str, texto: str) -> None:
    """Envía un mensaje de texto simple usando la WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto},
    }

    respuesta = requests.post(url, headers=headers, json=payload, timeout=15)
    print("Estado envío:", respuesta.status_code, respuesta.text)


def generar_respuesta(mensaje_usuario: str) -> str:
    """Define la lógica de respuestas según lo que escriba el usuario."""
    texto = mensaje_usuario.strip().lower()

    if texto in ("hola", "buenas", "menu", "menú"):
        return (
            "¡Hola! Soy un bot en Python.\n"
            "Escribe una opción:\n"
            "1. ayuda\n"
            "2. horario\n"
            "3. catalogo"
        )
    if texto == "1" or "ayuda" in texto:
        return "Escribe 'catalogo' para ver opciones o 'horario' para atención."
    if "horario" in texto:
        return "Atención automática 24/7. Respuesta humana de lunes a viernes de 8:00 a.m. a 5:00 p.m."
    if "catalogo" in texto or "catálogo" in texto:
        return "Consulta nuestro catálogo actualizado aquí: https://sixtovelarde.pages.dev/"

    return f"Recibí tu mensaje: '{mensaje_usuario}'. Escribe 'menu' para ver opciones."


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. Verificación inicial del webhook por parte de Meta (GET)
    if request.method == "GET":
        modo = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        reto = request.args.get("hub.challenge")

        if modo == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verificado correctamente.")
            return reto, 200
        return "Token de verificación inválido", 403

    # 2. Recepción de mensajes entrantes (POST)
    datos = request.get_json(silent=True) or {}
    print("Payload recibido:", datos)

    try:
        for entry in datos.get("entry", []):
            for change in entry.get("changes", []):
                valor = change.get("value", {})
                for mensaje in valor.get("messages", []):
                    if mensaje.get("type") == "text":
                        remitente = mensaje.get("from")
                        cuerpo = mensaje.get("text", {}).get("body", "")
                        respuesta = generar_respuesta(cuerpo)
                        enviar_mensaje_whatsapp(remitente, respuesta)
    except Exception as error:
        print("Error procesando mensaje:", error)

    # Meta espera un 200 OK rápido para no reintentar indefinidamente
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Ejecuta el servidor local en el puerto 5000
    app.run(host="0.0.0.0", port=5000, debug=True)