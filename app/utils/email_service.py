from flask import current_app
from flask_mail import Message
from app import mail


def enviar_correo_registro(destinatario, nombre):
    msg = Message(
        subject="Bienvenido a Lidera360",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        recipients=[destinatario]
    )

    msg.body = f"""
Hola {nombre},

Te has registrado correctamente en Lidera360.

Ahora puedes iniciar tu proceso de transformacion personal.

Equipo Lidera360
"""

    mail.send(msg)
