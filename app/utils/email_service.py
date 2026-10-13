from html import escape

from flask import current_app
import json
import urllib.error
import urllib.request


def _enviar_correo(destinatario, asunto, texto, html):
    """Envía un correo por la API HTTPS de Brevo (Render gratuito bloquea los puertos SMTP)."""
    api_key = current_app.config.get("BREVO_API_KEY")
    remitente = current_app.config.get("BREVO_SENDER_EMAIL")

    if not api_key:
        raise ValueError("BREVO_API_KEY no esta configurada")
    if not remitente:
        raise ValueError("BREVO_SENDER_EMAIL no esta configurada")

    payload = {
        "sender": {"name": current_app.config.get("BREVO_SENDER_NAME"), "email": remitente},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": texto,
        "htmlContent": html
    }

    request = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            # Cloudflare bloquea el User-Agent por defecto de urllib ("Python-urllib/3.x").
            "User-Agent": "Lidera360/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=current_app.config.get("EMAIL_TIMEOUT")) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8")
        raise RuntimeError(f"Brevo respondio {error.code}: {detalle}") from error


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


def _fecha_larga(fecha):
    if not fecha:
        return ""
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"


def _detalle_taller(datos):
    """Líneas con el detalle del taller: nivel, fechas y coach (las que existan)."""
    lineas = []
    if datos.get("nivel"):
        lineas.append(f"Nivel: {datos['nivel']}")
    if datos.get("fecha_inicio") and datos.get("fecha_fin"):
        lineas.append(f"Fechas: del {_fecha_larga(datos['fecha_inicio'])} al {_fecha_larga(datos['fecha_fin'])}")
    if datos.get("coach"):
        lineas.append(f"Coach: {datos['coach']}")
    return lineas


def _correo_con_parrafos(destinatario, asunto, nombre, parrafos, detalle=None):
    """Arma la versión de texto y HTML de un correo a partir de párrafos y un detalle opcional."""
    detalle = detalle or []
    url_portal = current_app.config.get("FRONTEND_URL")

    texto = "\n\n".join([f"Hola {nombre},", *parrafos])
    if detalle:
        texto += "\n\n" + "\n".join(detalle)
    texto += f"\n\nIngresa a tu portal: {url_portal}\n\nEquipo Lidera360\n"

    html = f"<p>Hola {escape(nombre)},</p>" + "".join(f"<p>{escape(parrafo)}</p>" for parrafo in parrafos)
    if detalle:
        html += "<ul>" + "".join(f"<li>{escape(linea)}</li>" for linea in detalle) + "</ul>"
    html += f'<p><a href="{url_portal}">Ingresar a mi portal</a></p><p>Equipo Lidera360</p>'

    return _enviar_correo(destinatario, asunto, texto, html)


def enviar_correo_inscripcion(datos):
    return _correo_con_parrafos(
        datos["correo"],
        f"Inscripción confirmada: {datos['taller']}",
        datos["nombres"],
        [f"Tu inscripción al taller {datos['taller']} quedó confirmada."],
        _detalle_taller(datos),
    )


def enviar_correo_resultado(datos, aprobado, nivel_nuevo=None, observacion=""):
    if aprobado:
        asunto = f"¡Aprobaste el taller {datos['taller']}!"
        parrafos = [f"¡Felicitaciones! Aprobaste el taller {datos['taller']}."]
        if nivel_nuevo:
            parrafos.append(f"Subiste al nivel {nivel_nuevo}. Ya puedes inscribirte en los talleres de ese nivel desde tu calendario.")
        elif datos.get("es_ultimo_nivel"):
            parrafos.append("Con este resultado completaste todos los niveles del programa Lidera360. ¡Gracias por tu compromiso!")
    else:
        asunto = f"Resultado del taller {datos['taller']}"
        parrafos = [
            f"Tu resultado en el taller {datos['taller']} fue: No aprobado.",
            "Puedes volver a inscribirte en un próximo taller de tu nivel desde el calendario de tu portal.",
        ]

    if observacion:
        parrafos.append(f"Comentario de tu coach: {observacion}")

    return _correo_con_parrafos(datos["correo"], asunto, datos["nombres"], parrafos)


def enviar_correo_cancelacion(datos):
    return _correo_con_parrafos(
        datos["correo"],
        f"Inscripción cancelada: {datos['taller']}",
        datos["nombres"],
        [
            f"Cancelaste tu inscripción al taller {datos['taller']}.",
            "Si fue un error, puedes volver a inscribirte desde el calendario mientras el taller siga disponible.",
        ],
    )
