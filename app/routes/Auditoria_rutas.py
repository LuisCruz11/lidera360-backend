from flask import Blueprint, jsonify
from app.controller.Auditoria_Controller import AuditoriaController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles


# La auditoría es de solo lectura: los registros los crea el sistema y no se pueden editar ni borrar.
auditoria_bp = Blueprint('auditoria_bp', __name__)


@auditoria_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_auditoria():
    return None


@auditoria_bp.route('/', methods=['GET'])
def obtener_auditorias():
    return jsonify(AuditoriaController.obtener_auditorias())


@auditoria_bp.route('/<int:id_auditoria>', methods=['GET'])
def obtener_auditoria(id_auditoria):
    auditoria = AuditoriaController.obtener_auditoria(id_auditoria)
    if auditoria:
        return jsonify(auditoria)
    return jsonify({"mensaje": "Auditoria no encontrada"}), 404
