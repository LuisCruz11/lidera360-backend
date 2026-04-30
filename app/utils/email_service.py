from flask import current_app
import json
import urllib.error
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

    html = f"""
<p>Hola {nombre},</p>
<p>Te has registrado correctamente en Lidera360.</p>
<p>Ahora puedes iniciar tu proceso de transformacion personal.</p>
<p>Equipo Lidera360</p>
"""

    payload = {
        "from": current_app.config.get("RESEND_FROM_EMAIL"),
        "to": [destinatario],
        "subject": "Bienvenido a Lidera360",
        "text": texto,
        "html": html
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

    try:
        with urllib.request.urlopen(
            request,
            timeout=current_app.config.get("RESEND_TIMEOUT")
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8")
        raise RuntimeError(f"Resend respondio {error.code}: {detalle}") from error
