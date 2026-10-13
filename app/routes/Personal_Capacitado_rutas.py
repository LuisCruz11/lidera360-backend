from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.controller.Personal_Capacitado_Controller import PersonalCapacitadoController
from app.utils.auth import ID_ROL_PERSONAL_CAPACITADO, requiere_roles
from app.utils.fechas import hoy


personal_capacitado_bp = Blueprint('personal_capacitado_bp', __name__)


@personal_capacitado_bp.before_request
@requiere_roles(ID_ROL_PERSONAL_CAPACITADO)
def _restringir_personal_capacitado():
    return None


def _cedula_personal():
    return get_jwt().get("cedula_personal")


def _respuesta_error(error):
    if isinstance(error, PermissionError):
        return jsonify({"mensaje": str(error)}), 403
    if isinstance(error, LookupError):
        return jsonify({"mensaje": str(error)}), 404
    return jsonify({"mensaje": str(error)}), 400


@personal_capacitado_bp.route('/talleres', methods=['GET'])
def obtener_talleres():
    try:
        return jsonify(PersonalCapacitadoController.obtener_talleres(_cedula_personal()))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@personal_capacitado_bp.route('/clientes', methods=['GET'])
def obtener_clientes():
    try:
        return jsonify(PersonalCapacitadoController.obtener_clientes(_cedula_personal()))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@personal_capacitado_bp.route('/talleres/<int:id_taller>', methods=['GET'])
def obtener_detalle_taller(id_taller):
    try:
        return jsonify(PersonalCapacitadoController.obtener_detalle_taller(id_taller, _cedula_personal()))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@personal_capacitado_bp.route('/talleres/<int:id_taller>/notas', methods=['POST'])
def agregar_nota(id_taller):
    data = request.get_json(silent=True) or {}
    try:
        id_nota = PersonalCapacitadoController.agregar_nota(id_taller, _cedula_personal(), get_jwt_identity(), data)
        return jsonify({"mensaje": "Nota agregada", "id_auditoria": id_nota}), 201
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@personal_capacitado_bp.route('/talleres/<int:id_taller>/asistencia', methods=['GET'])
def obtener_asistencia(id_taller):
    fecha = request.args.get('fecha') or hoy().isoformat()
    try:
        return jsonify(PersonalCapacitadoController.obtener_asistencia(id_taller, _cedula_personal(), fecha))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@personal_capacitado_bp.route('/talleres/<int:id_taller>/asistencia', methods=['PUT'])
def registrar_asistencia(id_taller):
    data = request.get_json(silent=True) or {}
    try:
        presentes, total = PersonalCapacitadoController.registrar_asistencia(
            id_taller, _cedula_personal(), get_jwt_identity(), data
        )
        return jsonify({"mensaje": "Asistencia registrada", "presentes": presentes, "total": total})
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)
