from flask import Blueprint, request, jsonify
from app.controller.Estado_Controller import EstadoController


estado_bp = Blueprint('estado_bp', __name__)


@estado_bp.route('/', methods=['GET'])
def obtener_estados():
    return jsonify(EstadoController.obtener_estados())


@estado_bp.route('/<int:id_estado>', methods=['GET'])
def obtener_estado(id_estado):
    estado = EstadoController.obtener_estado(id_estado)
    if estado:
        return jsonify(estado)
    return jsonify({"mensaje": "Estado no encontrado"}), 404


@estado_bp.route('/', methods=['POST'])
def crear_estado():
    data = request.json
    id_estado = EstadoController.crear_estado(data)
    return jsonify({"mensaje": "Estado creado", "id_estado": id_estado}), 201


@estado_bp.route('/<int:id_estado>', methods=['PUT'])
def actualizar_estado(id_estado):
    data = request.json
    actualizado = EstadoController.actualizar_estado(id_estado, data)
    if actualizado:
        return jsonify({"mensaje": "Estado actualizado"})
    return jsonify({"mensaje": "Estado no encontrado"}), 404


@estado_bp.route('/<int:id_estado>', methods=['DELETE'])
def eliminar_estado(id_estado):
    eliminado = EstadoController.eliminar_estado(id_estado)
    if eliminado:
        return jsonify({"mensaje": "Estado eliminado"})
    return jsonify({"mensaje": "Estado no encontrado"}), 404
