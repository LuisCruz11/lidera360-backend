import re

REGEX_SOLO_LETRAS = re.compile(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+$')
REGEX_CEDULA = re.compile(r'^\d{6,10}$')
REGEX_TELEFONO = re.compile(r'^\d{7,10}$')
REGEX_CORREO = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
REGEX_PASSWORD = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%?&])[A-Za-z\d@$!%?&]{8,}$')


def validar_cedula(cedula):
    if not cedula or not REGEX_CEDULA.match(str(cedula)):
        raise ValueError("La cédula debe contener solo números, entre 6 y 10 dígitos")


def validar_nombre(valor, etiqueta="El nombre"):
    if not valor or not REGEX_SOLO_LETRAS.match(valor):
        raise ValueError(f"{etiqueta} solo puede contener letras y espacios")


def validar_telefono(telefono, obligatorio=False):
    if not telefono:
        if obligatorio:
            raise ValueError("El teléfono es obligatorio")
        return
    if not REGEX_TELEFONO.match(str(telefono)):
        raise ValueError("El teléfono debe contener solo números, entre 7 y 10 dígitos")


def validar_correo(correo, obligatorio=False):
    if not correo:
        if obligatorio:
            raise ValueError("El correo es obligatorio")
        return
    if not REGEX_CORREO.match(correo):
        raise ValueError("El correo no tiene un formato válido")


def validar_password(password):
    if not password or not REGEX_PASSWORD.match(password):
        raise ValueError(
            "La contraseña debe tener mínimo 8 caracteres, una letra mayúscula, "
            "una letra minúscula, un número y un carácter especial (@$!%?&)"
        )


def validar_edad(edad):
    try:
        valor = int(edad)
    except (TypeError, ValueError):
        raise ValueError("La edad debe ser un número")
    if valor <= 0 or valor > 120:
        raise ValueError("La edad debe estar entre 1 y 120")
