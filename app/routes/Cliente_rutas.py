from flask import Blueprint, request, jsonify
from app.controller.Cliente_Controller import ClienteController

cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/', methods=['GET'])
def obtener_clientes():
    return jsonify(ClienteController.obtener_clientes())

@cliente_bp.route('/<cedula>', methods=['GET'])
def obtener_cliente(cedula):
    cliente = ClienteController.obtener_cliente(cedula)
    if cliente:
        return jsonify(cliente)
    return jsonify({"mensaje": "Cliente no encontrado"}), 404

@cliente_bp.route('/<cedula>/panel', methods=['GET'])
def obtener_panel_cliente(cedula):
    panel = ClienteController.obtener_panel_cliente(cedula)
    if panel:
        return jsonify(panel)
    return jsonify({"mensaje": "Cliente no encontrado"}), 404

@cliente_bp.route('/<cedula>/inscripciones', methods=['POST'])
def inscribir_cliente_en_taller(cedula):
    data = request.get_json(silent=True) or {}
    try:
        id_inscripcion = ClienteController.inscribir_en_taller(cedula, data)
        return jsonify({
            "mensaje": "Inscripcion creada",
            "id_inscripcion": id_inscripcion
        }), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400

@cliente_bp.route('/', methods=['POST'])
def crear_cliente():
    data = request.get_json(silent=True) or {}
    campos_requeridos = ['cedula', 'nombres', 'apellidos', 'sexo', 'edad', 'id_estado']
    campos_faltantes = [
        campo for campo in campos_requeridos
        if campo not in data or data[campo] in (None, '')
    ]

    if campos_faltantes:
        return jsonify({
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    sexos_validos = ['M', 'F', 'Otro']
    if data['sexo'] not in sexos_validos:
        return jsonify({
            "mensaje": "El sexo debe ser M, F u Otro"
        }), 400

    try:
        ClienteController.crear_cliente(data)
        return jsonify({"mensaje": "Cliente creado"}), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 409

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
