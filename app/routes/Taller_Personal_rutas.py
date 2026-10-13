from flask import Blueprint, request, jsonify
from app.controller.Taller_Personal_Controller import TallerPersonalController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles
from app.utils.auditoria import auditar
import app.utils.descripciones_auditoria as da


taller_personal_bp = Blueprint('taller_personal_bp', __name__)


@taller_personal_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_taller_personal():
    return None


@taller_personal_bp.route('/', methods=['GET'])
def obtener_taller_personal_lista():
    return jsonify(TallerPersonalController.obtener_taller_personal_lista())


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['GET'])
def obtener_taller_personal(id_taller_personal):
    registro = TallerPersonalController.obtener_taller_personal(id_taller_personal)
    if registro:
        return jsonify(registro)
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404


@taller_personal_bp.route('/', methods=['POST'])
@auditar("taller_personal", "crear", da.asignacion_guardada, taller=da.taller_de_los_datos)
def crear_taller_personal():
    data = request.json
    id_taller_personal = TallerPersonalController.crear_taller_personal(data)
    return jsonify({"mensaje": "Taller personal creado", "id_taller_personal": id_taller_personal}), 201


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['PUT'])
@auditar("taller_personal", "actualizar", da.asignacion_guardada, taller=da.taller_de_los_datos)
def actualizar_taller_personal(id_taller_personal):
    data = request.json
    actualizado = TallerPersonalController.actualizar_taller_personal(id_taller_personal, data)
    if actualizado:
        return jsonify({"mensaje": "Taller personal actualizado"})
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['DELETE'])
@auditar("taller_personal", "eliminar", da.asignacion_eliminada, antes=da.antes_de_eliminar_asignacion, taller=da.taller_de_los_datos)
def eliminar_taller_personal(id_taller_personal):
    eliminado = TallerPersonalController.eliminar_taller_personal(id_taller_personal)
    if eliminado:
        return jsonify({"mensaje": "Taller personal eliminado"})
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404
