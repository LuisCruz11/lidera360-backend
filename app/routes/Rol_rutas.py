from flask import Blueprint, request, jsonify
from app.controller.Rol_Controller import RolController


rol_bp = Blueprint('rol_bp', __name__)


@rol_bp.route('/', methods=['GET'])
def obtener_roles():
    return jsonify(RolController.obtener_roles())


@rol_bp.route('/<int:id_rol>', methods=['GET'])
def obtener_rol(id_rol):
    rol = RolController.obtener_rol(id_rol)
    if rol:
        return jsonify(rol)
    return jsonify({"mensaje": "Rol no encontrado"}), 404


@rol_bp.route('/', methods=['POST'])
def crear_rol():
    data = request.json
    id_rol = RolController.crear_rol(data)
    return jsonify({"mensaje": "Rol creado", "id_rol": id_rol}), 201


@rol_bp.route('/<int:id_rol>', methods=['PUT'])
def actualizar_rol(id_rol):
    data = request.json
    actualizado = RolController.actualizar_rol(id_rol, data)
    if actualizado:
        return jsonify({"mensaje": "Rol actualizado"})
    return jsonify({"mensaje": "Rol no encontrado"}), 404


@rol_bp.route('/<int:id_rol>', methods=['DELETE'])
def eliminar_rol(id_rol):
    eliminado = RolController.eliminar_rol(id_rol)
    if eliminado:
        return jsonify({"mensaje": "Rol eliminado"})
    return jsonify({"mensaje": "Rol no encontrado"}), 404
