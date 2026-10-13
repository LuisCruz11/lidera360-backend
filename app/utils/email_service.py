from flask import current_app
import json
import urllib.error
import urllib.request


def _post_json(url, payload, headers, proveedor):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            # Cloudflare (delante de estas APIs) bloquea el User-Agent por defecto
            # de urllib ("Python-urllib/3.x") con el error 1010.
            "User-Agent": "Lidera360/1.0",
            **headers
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=current_app.config.get("RESEND_TIMEOUT")
        ) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8")
        raise RuntimeError(f"{proveedor} respondio {error.code}: {detalle}") from error


def _enviar_con_brevo(api_key, destinatario, asunto, texto, html):
    remitente = current_app.config.get("BREVO_SENDER_EMAIL")
    if not remitente:
        raise ValueError("BREVO_SENDER_EMAIL no esta configurada")

    payload = {
        "sender": {"name": current_app.config.get("BREVO_SENDER_NAME"), "email": remitente},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": texto,
        "htmlContent": html
    }
    return _post_json("https://api.brevo.com/v3/smtp/email", payload, {"api-key": api_key}, "Brevo")


def _enviar_con_resend(api_key, destinatario, asunto, texto, html):
    payload = {
        "from": current_app.config.get("RESEND_FROM_EMAIL"),
        "to": [destinatario],
        "subject": asunto,
        "text": texto,
        "html": html
    }
    return _post_json("https://api.resend.com/emails", payload, {"Authorization": f"Bearer {api_key}"}, "Resend")


def _enviar_correo(destinatario, asunto, texto, html):
    # Brevo permite usar como remitente un Gmail verificado (sin dominio propio);
    # si no está configurado, se usa Resend.
    brevo_api_key = current_app.config.get("BREVO_API_KEY")
    if brevo_api_key:
        return _enviar_con_brevo(brevo_api_key, destinatario, asunto, texto, html)

    resend_api_key = current_app.config.get("RESEND_API_KEY")
    if resend_api_key:
        return _enviar_con_resend(resend_api_key, destinatario, asunto, texto, html)

    raise ValueError("No hay un proveedor de correo configurado (BREVO_API_KEY o RESEND_API_KEY)")


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
