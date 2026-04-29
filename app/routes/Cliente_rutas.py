from flask import Blueprint, request, jsonify
from app.controller.Cliente_Controller import ClienteController

cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/', methods=['GET'])
def obtener_clientes():
    return jsonify(ClienteController.obtener_clientes())

@cliente_bp.route('/<cedula>', methods=['GET'])
def obtener_cliente(cedula):
    return jsonify(ClienteController.obtener_cliente(cedula))

@cliente_bp.route('/', methods=['POST'])
def crear_cliente():
    data = request.json
    ClienteController.crear_cliente(data)
    return jsonify({"mensaje": "Cliente creado"}), 201

@cliente_bp.route('/<cedula>', methods=['PUT'])
def actualizar_cliente(cedula):
    data = request.json
    actualizado = ClienteController.actualizar_cliente(cedula, data)
    if actualizado:
        return jsonify({"mensaje": "Cliente actualizado"})
    return jsonify({"mensaje": "Cliente no encontrado"}), 404

@cliente_bp.route('/<cedula>', methods=['DELETE'])
def eliminar_cliente(cedula):
    eliminado = ClienteController.eliminar_cliente(cedula)
    if eliminado:
        return jsonify({"mensaje": "Cliente eliminado"})
    return jsonify({"mensaje": "Cliente no encontrado"}), 404
