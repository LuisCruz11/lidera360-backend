from flask import current_app
import json
import urllib.error
import urllib.request


def _enviar_correo(destinatario, asunto, texto, html):
    api_key = current_app.config.get("RESEND_API_KEY")

    if not api_key:
        raise ValueError("RESEND_API_KEY no esta configurada")

    payload = {
        "from": current_app.config.get("RESEND_FROM_EMAIL"),
        "to": [destinatario],
        "subject": asunto,
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


def enviar_correo_registro(destinatario, nombre):
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

    return _enviar_correo(destinatario, "Bienvenido a Lidera360", texto, html)


def enviar_correo_recuperacion(destinatario, nombre, enlace):
    texto = f"""
Hola {nombre},

Recibimos una solicitud para restablecer tu contraseña de Lidera360.

Abre este enlace para crear una nueva (vence en 30 minutos):
{enlace}

Si no fuiste tú, ignora este correo: tu contraseña no cambiará.

Equipo Lidera360
"""

    html = f"""
<p>Hola {nombre},</p>
<p>Recibimos una solicitud para restablecer tu contraseña de Lidera360.</p>
<p><a href="{enlace}">Crear una nueva contraseña</a> (el enlace vence en 30 minutos).</p>
<p>Si no fuiste tú, ignora este correo: tu contraseña no cambiará.</p>
<p>Equipo Lidera360</p>
"""

    return _enviar_correo(destinatario, "Restablece tu contraseña de Lidera360", texto, html)
