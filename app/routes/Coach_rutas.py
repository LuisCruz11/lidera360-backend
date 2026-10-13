from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.controller.Coach_Controller import CoachController
from app.utils.auth import ID_ROL_COACH, requiere_roles


coach_bp = Blueprint('coach_bp', __name__)


@coach_bp.before_request
@requiere_roles(ID_ROL_COACH)
def _restringir_coach():
    return None


def _cedula_personal():
    return get_jwt().get("cedula_personal")


def _respuesta_error(error):
    if isinstance(error, PermissionError):
        return jsonify({"mensaje": str(error)}), 403
    if isinstance(error, LookupError):
        return jsonify({"mensaje": str(error)}), 404
    return jsonify({"mensaje": str(error)}), 400


@coach_bp.route('/talleres', methods=['GET'])
def obtener_talleres():
    try:
        return jsonify(CoachController.obtener_talleres(_cedula_personal()))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@coach_bp.route('/talleres/<int:id_taller>', methods=['GET'])
def obtener_detalle_taller(id_taller):
    try:
        return jsonify(CoachController.obtener_detalle_taller(id_taller, _cedula_personal()))
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@coach_bp.route('/talleres/<int:id_taller>/actividades', methods=['POST'])
def registrar_actividad(id_taller):
    data = request.get_json(silent=True) or {}
    try:
        id_actividad = CoachController.registrar_actividad(id_taller, _cedula_personal(), get_jwt_identity(), data)
        return jsonify({"mensaje": "Actividad registrada", "id_auditoria": id_actividad}), 201
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)


@coach_bp.route('/inscripciones/<int:id_inscripcion>/evaluacion', methods=['PUT'])
def evaluar_participante(id_inscripcion):
    data = request.get_json(silent=True) or {}
    try:
        CoachController.evaluar_participante(id_inscripcion, _cedula_personal(), get_jwt_identity(), data)
        return jsonify({"mensaje": "Evaluación registrada"})
    except (PermissionError, LookupError, ValueError) as error:
        return _respuesta_error(error)
