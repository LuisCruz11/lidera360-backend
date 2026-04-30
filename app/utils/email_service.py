from flask import current_app
import json
import urllib.request


def enviar_correo_registro(destinatario, nombre):
    api_key = current_app.config.get("RESEND_API_KEY")

    if not api_key:
        raise ValueError("RESEND_API_KEY no esta configurada")

    texto = f"""
Hola {nombre},

Te has registrado correctamente en Lidera360.

Ahora puedes iniciar tu proceso de transformacion personal.

Equipo Lidera360
"""

    payload = {
        "from": current_app.config.get("RESEND_FROM_EMAIL"),
        "to": [destinatario],
        "subject": "Bienvenido a Lidera360",
        "text": texto
    }

    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=current_app.config.get("RESEND_TIMEOUT")
    ) as response:
        return json.loads(response.read().decode("utf-8"))
