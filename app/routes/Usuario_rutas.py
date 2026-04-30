from flask import Blueprint, request, jsonify
from app.controller.Usuario_Controller import UsuarioController

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/', methods=['GET'])
def obtener_usuarios():
    return jsonify(UsuarioController.obtener_usuarios())

@usuario_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    usuario = UsuarioController.obtener_usuario(id_usuario)
    if usuario:
        return jsonify(usuario)
    return jsonify({"mensaje": "Usuario no encontrado"}), 404

@usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = UsuarioController.login(data)

    if usuario:
        return jsonify(usuario)

    return jsonify({"mensaje": "Credenciales incorrectas"}), 401

@usuario_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json(silent=True) or {}

    campos_requeridos = [
        'cedula',
        'nombres',
        'apellidos',
        'correo',
        'telefono',
        'sexo',
        'edad',
        'username',
        'password'
    ]

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
        correo_enviado = UsuarioController.registrar_cliente_usuario(data)
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 409

    if not correo_enviado:
        return jsonify({
            "mensaje": "Usuario registrado correctamente, pero no se pudo enviar el correo"
        }), 201

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201

@usuario_bp.route('/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    data = request.json
    actualizado = UsuarioController.actualizar_usuario(id_usuario, data)
    if actualizado:
        return jsonify({"mensaje": "Usuario actualizado"})
    return jsonify({"mensaje": "Usuario no encontrado"}), 404

@usuario_bp.route('/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    eliminado = UsuarioController.eliminar_usuario(id_usuario)
    if eliminado:
        return jsonify({"mensaje": "Usuario eliminado"})
    return jsonify({"mensaje": "Usuario no encontrado"}), 404
