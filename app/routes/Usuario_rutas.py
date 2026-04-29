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

@usuario_bp.route('/', methods=['POST'])
def crear_usuario():
    data = request.json
    id_usuario = UsuarioController.crear_usuario(data)
    return jsonify({"mensaje": "Usuario creado", "id_usuario": id_usuario}), 201

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
