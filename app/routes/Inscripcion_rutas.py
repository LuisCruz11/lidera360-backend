from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.controller.Inscripcion_Controller import InscripcionController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles
from app.utils.auditoria import auditar
import app.utils.descripciones_auditoria as da


inscripcion_bp = Blueprint('inscripcion_bp', __name__)


@inscripcion_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_inscripcion():
    return None


@inscripcion_bp.route('/', methods=['GET'])
def obtener_inscripciones():
    return jsonify(InscripcionController.obtener_inscripciones())


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['GET'])
def obtener_inscripcion(id_inscripcion):
    inscripcion = InscripcionController.obtener_inscripcion(id_inscripcion)
    if inscripcion:
        return jsonify(inscripcion)
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404


@inscripcion_bp.route('/', methods=['POST'])
@auditar("inscripcion", "crear", da.inscripcion_creada, taller=da.taller_de_los_datos)
def crear_inscripcion():
    data = request.get_json(silent=True) or {}
    campos_requeridos = ['cliente_cedula', 'id_taller', 'id_estado']
    campos_faltantes = [
        campo for campo in campos_requeridos
        if campo not in data or data[campo] in (None, '')
    ]

    if campos_faltantes:
        return jsonify({
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:
        id_inscripcion, nivel_nuevo = InscripcionController.crear_inscripcion(data, get_jwt_identity())
        return jsonify({
            "mensaje": "Inscripcion creada",
            "id_inscripcion": id_inscripcion,
            "nivel_nuevo": nivel_nuevo
        }), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 409


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['PUT'])
@auditar("inscripcion", "actualizar", da.inscripcion_actualizada, antes=da.antes_de_modificar_inscripcion, taller=da.taller_de_los_datos)
def actualizar_inscripcion(id_inscripcion):
    data = request.get_json(silent=True) or {}
    actualizado, nivel_nuevo = InscripcionController.actualizar_inscripcion(id_inscripcion, data, get_jwt_identity())
    if actualizado:
        return jsonify({"mensaje": "Inscripcion actualizada", "nivel_nuevo": nivel_nuevo})
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['DELETE'])
@auditar("inscripcion", "eliminar", da.inscripcion_eliminada, antes=da.antes_de_modificar_inscripcion, taller=da.taller_de_los_datos)
def eliminar_inscripcion(id_inscripcion):
    eliminado = InscripcionController.eliminar_inscripcion(id_inscripcion)
    if eliminado:
        return jsonify({"mensaje": "Inscripcion eliminada"})
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404
