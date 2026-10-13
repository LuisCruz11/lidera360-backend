"""Registro de auditoría de las acciones del coordinador.

Uso en una ruta (debajo de @route y de @requiere_roles):

    @auditar("clientes", "crear", lambda c: f"Creó el cliente {c.datos.get('cedula')}")

El registro se guarda solo si la ruta respondió con éxito (2xx). Si guardar la auditoría
falla, la acción del usuario no se revierte: el error queda en el log.
"""
from functools import wraps
from types import SimpleNamespace

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.models.dao.Auditoria_DAO import AuditoriaDAO
from app.models.dto.Auditoria_DTO import AuditoriaDTO


def registrar(tabla, accion, descripcion, id_taller=None):
    try:
        AuditoriaDAO.crear(AuditoriaDTO(None, get_jwt_identity(), tabla, accion, descripcion, None, id_taller))
    except Exception as error:
        print(f"No se pudo registrar la auditoría ({tabla}/{accion}): {error}", flush=True)


def _codigo_y_cuerpo(respuesta):
    if isinstance(respuesta, tuple):
        objeto, codigo = respuesta[0], respuesta[1]
    else:
        objeto, codigo = respuesta, getattr(respuesta, "status_code", 200)
    cuerpo = objeto.get_json(silent=True) if hasattr(objeto, "get_json") and objeto.is_json else {}
    return codigo, cuerpo or {}


def auditar(tabla, accion, describir, antes=None, taller=None):
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            datos = request.get_json(silent=True) or {}
            previo = {}
            if antes:
                try:
                    previo = antes(**kwargs) or {}
                except Exception as error:
                    print(f"No se pudo preparar la auditoría ({tabla}/{accion}): {error}", flush=True)

            respuesta = vista(*args, **kwargs)

            codigo, cuerpo = _codigo_y_cuerpo(respuesta)
            if 200 <= codigo < 300:
                contexto = SimpleNamespace(
                    ruta=kwargs, datos=datos, previo=previo, respuesta=cuerpo, parametros=request.args.to_dict()
                )
                try:
                    descripcion = describir(contexto)
                    id_taller = taller(contexto) if taller else None
                except Exception as error:
                    print(f"No se pudo describir la auditoría ({tabla}/{accion}): {error}", flush=True)
                    descripcion, id_taller = f"{accion} en {tabla}", None
                registrar(tabla, accion, descripcion, id_taller)
            return respuesta
        return envoltura
    return decorador


def nombre_persona(registro):
    if registro is None:
        return ""
    obtener = registro.get if isinstance(registro, dict) else lambda campo: getattr(registro, campo, None)
    return f"{obtener('nombres') or ''} {obtener('apellidos') or ''}".strip()
