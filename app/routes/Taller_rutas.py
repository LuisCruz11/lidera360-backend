from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.controller.Taller_Controller import TallerController
from app.utils.auth import ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO, requiere_roles


taller_bp = Blueprint('taller_bp', __name__)


@taller_bp.route('/', methods=['GET'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO)
def obtener_talleres():
    return jsonify(TallerController.obtener_talleres())


@taller_bp.route('/<int:id_taller>', methods=['GET'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO)
def obtener_taller(id_taller):
    taller = TallerController.obtener_taller(id_taller)
    if taller:
        return jsonify(taller)
    return jsonify({"mensaje": "Taller no encontrado"}), 404


@taller_bp.route('/<int:id_taller>/detalle', methods=['GET'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO)
def obtener_detalle_taller(id_taller):
    detalle = TallerController.obtener_detalle(id_taller)
    if detalle:
        return jsonify(detalle)
    return jsonify({"mensaje": "Taller no encontrado"}), 404


@taller_bp.route('/<int:id_taller>/notas', methods=['POST'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO)
def agregar_nota_taller(id_taller):
    data = request.get_json(silent=True) or {}
    try:
        id_nota = TallerController.agregar_nota(id_taller, get_jwt_identity(), data)
        return jsonify({"mensaje": "Nota agregada", "id_auditoria": id_nota}), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400


@taller_bp.route('/', methods=['POST'])
@requiere_roles(ID_ROL_COORDINADOR)
def crear_taller():
    data = request.get_json(silent=True) or {}
    campos_requeridos = ['nombre', 'id_tipo_taller', 'fecha_inicio', 'fecha_fin', 'id_estado']
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
        id_taller = TallerController.crear_taller(data)
        return jsonify({"mensaje": "Taller creado", "id_taller": id_taller}), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400


@taller_bp.route('/<int:id_taller>', methods=['PUT'])
@requiere_roles(ID_ROL_COORDINADOR)
def actualizar_taller(id_taller):
    data = request.get_json(silent=True) or {}
    campos_requeridos = ['nombre', 'id_tipo_taller', 'fecha_inicio', 'fecha_fin', 'id_estado']
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
        actualizado = TallerController.actualizar_taller(id_taller, data)
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400
    if actualizado:
        return jsonify({"mensaje": "Taller actualizado"})
    return jsonify({"mensaje": "Taller no encontrado"}), 404


@taller_bp.route('/<int:id_taller>', methods=['DELETE'])
@requiere_roles(ID_ROL_COORDINADOR)
def eliminar_taller(id_taller):
    try:
        eliminado = TallerController.eliminar_taller(id_taller)
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 409
    if eliminado:
        return jsonify({"mensaje": "Taller eliminado"})
    return jsonify({"mensaje": "Taller no encontrado"}), 404
