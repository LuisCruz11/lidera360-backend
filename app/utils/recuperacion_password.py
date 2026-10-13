import hashlib

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SALT = "lidera360-recuperar-password"
VIGENCIA_SEGUNDOS = 30 * 60


def _serializador():
    return URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"], salt=SALT)


def _huella(password_cifrado):
    # Huella de la contraseña actual: al cambiarla, cualquier enlace emitido antes deja de servir.
    return hashlib.sha256(password_cifrado.encode("utf-8")).hexdigest()[:16]


def generar_token(id_usuario, password_cifrado):
    return _serializador().dumps({"u": id_usuario, "h": _huella(password_cifrado)})


def leer_token(token):
    """Devuelve (id_usuario, huella) o lanza ValueError si el token es inválido o venció."""
    try:
        datos = _serializador().loads(token, max_age=VIGENCIA_SEGUNDOS)
    except SignatureExpired:
        raise ValueError("El enlace de recuperación venció. Solicita uno nuevo.")
    except BadSignature:
        raise ValueError("El enlace de recuperación no es válido.")
    return datos.get("u"), datos.get("h")


def huella_coincide(password_cifrado, huella):
    return _huella(password_cifrado) == huella
