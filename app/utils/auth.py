from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity

ID_ROL_COACH = 2
ID_ROL_PERSONAL_CAPACITADO = 3
ID_ROL_CLIENTE = 4
ID_ROL_COORDINADOR = 5


def _rol_actual():
    return get_jwt().get("id_rol")


def requiere_roles(*roles_permitidos):
    """Restringe una ruta a usuarios cuyo id_rol esté en roles_permitidos."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if _rol_actual() not in roles_permitidos:
                return jsonify({"mensaje": "No tienes permisos para realizar esta acción"}), 403
            return vista(*args, **kwargs)
        return envoltura
    return decorador


def requiere_propio_usuario(vista):
    """Permite al coordinador o al dueño del id_usuario de la ruta."""
    @wraps(vista)
    def envoltura(id_usuario, *args, **kwargs):
        if _rol_actual() == ID_ROL_COORDINADOR or str(get_jwt_identity()) == str(id_usuario):
            return vista(id_usuario, *args, **kwargs)
        return jsonify({"mensaje": "No tienes permisos para acceder a esta información"}), 403
    return envoltura


def requiere_propio_cliente(vista):
    """Permite al coordinador o al cliente dueño de la cedula de la ruta."""
    @wraps(vista)
    def envoltura(cedula, *args, **kwargs):
        claims = get_jwt()
        if claims.get("id_rol") == ID_ROL_COORDINADOR:
            return vista(cedula, *args, **kwargs)
        if claims.get("id_rol") == ID_ROL_CLIENTE and str(claims.get("cedula_cliente")) == str(cedula):
            return vista(cedula, *args, **kwargs)
        return jsonify({"mensaje": "No tienes permisos para acceder a esta información"}), 403
    return envoltura
