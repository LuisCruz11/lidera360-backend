from flask import Blueprint, request, jsonify
from app.controller.Estado_Controller import EstadoController
from app.utils.auth import ID_ROL_COACH, ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO, requiere_roles
from app.utils.auditoria import auditar
import app.utils.descripciones_auditoria as da
from app.models.dao.Estado_DAO import EstadoDAO


estado_bp = Blueprint('estado_bp', __name__)


@estado_bp.route('/', methods=['GET'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO, ID_ROL_COACH)
def obtener_estados():
    try:
        return jsonify(EstadoController.obtener_estados(request.args.get('aplica_a')))
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400


@estado_bp.route('/<int:id_estado>', methods=['GET'])
@requiere_roles(ID_ROL_COORDINADOR, ID_ROL_PERSONAL_CAPACITADO, ID_ROL_COACH)
def obtener_estado(id_estado):
    estado = EstadoController.obtener_estado(id_estado)
    if estado:
        return jsonify(estado)
    return jsonify({"mensaje": "Estado no encontrado"}), 404


@estado_bp.route('/', methods=['POST'])
@requiere_roles(ID_ROL_COORDINADOR)
@auditar("estados", "crear", da.catalogo_creado("estado"))
def crear_estado():
    data = request.get_json(silent=True) or {}
    try:
        id_estado = EstadoController.crear_estado(data)
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400
    return jsonify({"mensaje": "Estado creado", "id_estado": id_estado}), 201


@estado_bp.route('/<int:id_estado>', methods=['PUT'])
@requiere_roles(ID_ROL_COORDINADOR)
@auditar("estados", "actualizar", da.catalogo_actualizado("estado", "id_estado"))
def actualizar_estado(id_estado):
    data = request.get_json(silent=True) or {}
    try:
        actualizado = EstadoController.actualizar_estado(id_estado, data)
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400
    if actualizado:
        return jsonify({"mensaje": "Estado actualizado"})
    return jsonify({"mensaje": "Estado no encontrado"}), 404


@estado_bp.route('/<int:id_estado>', methods=['DELETE'])
@requiere_roles(ID_ROL_COORDINADOR)
@auditar("estados", "eliminar", da.catalogo_eliminado("estado", "id_estado"), antes=da.antes_de_eliminar_catalogo(EstadoDAO, "id_estado"))
def eliminar_estado(id_estado):
    eliminado = EstadoController.eliminar_estado(id_estado)
    if eliminado:
        return jsonify({"mensaje": "Estado eliminado"})
    return jsonify({"mensaje": "Estado no encontrado"}), 404
