from flask import Blueprint, request, jsonify
from app.controller.Progreso_Cliente_Controller import ProgresoClienteController


progreso_cliente_bp = Blueprint('progreso_cliente_bp', __name__)


@progreso_cliente_bp.route('/', methods=['GET'])
def obtener_progresos():
    return jsonify(ProgresoClienteController.obtener_progresos())


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['GET'])
def obtener_progreso(id_progreso):
    progreso = ProgresoClienteController.obtener_progreso(id_progreso)
    if progreso:
        return jsonify(progreso)
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/cliente/<cliente_cedula>', methods=['GET'])
def obtener_progreso_por_cliente(cliente_cedula):
    progreso = ProgresoClienteController.obtener_progreso_por_cliente(cliente_cedula)
    if progreso:
        return jsonify(progreso)
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/', methods=['POST'])
def crear_progreso():
    data = request.json
    id_progreso = ProgresoClienteController.crear_progreso(data)
    return jsonify({"mensaje": "Progreso creado", "id_progreso": id_progreso}), 201


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['PUT'])
def actualizar_progreso(id_progreso):
    data = request.json
    actualizado = ProgresoClienteController.actualizar_progreso(id_progreso, data)
    if actualizado:
        return jsonify({"mensaje": "Progreso actualizado"})
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['DELETE'])
def eliminar_progreso(id_progreso):
    eliminado = ProgresoClienteController.eliminar_progreso(id_progreso)
    if eliminado:
        return jsonify({"mensaje": "Progreso eliminado"})
    return jsonify({"mensaje": "Progreso no encontrado"}), 404
