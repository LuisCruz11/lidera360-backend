from flask import Blueprint, request, jsonify
from app.controller.Auditoria_Controller import AuditoriaController


auditoria_bp = Blueprint('auditoria_bp', __name__)


@auditoria_bp.route('/', methods=['GET'])
def obtener_auditorias():
    return jsonify(AuditoriaController.obtener_auditorias())


@auditoria_bp.route('/<int:id_auditoria>', methods=['GET'])
def obtener_auditoria(id_auditoria):
    auditoria = AuditoriaController.obtener_auditoria(id_auditoria)
    if auditoria:
        return jsonify(auditoria)
    return jsonify({"mensaje": "Auditoria no encontrada"}), 404


@auditoria_bp.route('/', methods=['POST'])
def crear_auditoria():
    data = request.json
    id_auditoria = AuditoriaController.crear_auditoria(data)
    return jsonify({"mensaje": "Auditoria creada", "id_auditoria": id_auditoria}), 201


@auditoria_bp.route('/<int:id_auditoria>', methods=['PUT'])
def actualizar_auditoria(id_auditoria):
    data = request.json
    actualizado = AuditoriaController.actualizar_auditoria(id_auditoria, data)
    if actualizado:
        return jsonify({"mensaje": "Auditoria actualizada"})
    return jsonify({"mensaje": "Auditoria no encontrada"}), 404


@auditoria_bp.route('/<int:id_auditoria>', methods=['DELETE'])
def eliminar_auditoria(id_auditoria):
    eliminado = AuditoriaController.eliminar_auditoria(id_auditoria)
    if eliminado:
        return jsonify({"mensaje": "Auditoria eliminada"})
    return jsonify({"mensaje": "Auditoria no encontrada"}), 404
