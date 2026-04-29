from flask import Blueprint, request, jsonify
from app.controller.Taller_Personal_Controller import TallerPersonalController


taller_personal_bp = Blueprint('taller_personal_bp', __name__)


@taller_personal_bp.route('/', methods=['GET'])
def obtener_taller_personal_lista():
    return jsonify(TallerPersonalController.obtener_taller_personal_lista())


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['GET'])
def obtener_taller_personal(id_taller_personal):
    registro = TallerPersonalController.obtener_taller_personal(id_taller_personal)
    if registro:
        return jsonify(registro)
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404


@taller_personal_bp.route('/', methods=['POST'])
def crear_taller_personal():
    data = request.json
    id_taller_personal = TallerPersonalController.crear_taller_personal(data)
    return jsonify({"mensaje": "Taller personal creado", "id_taller_personal": id_taller_personal}), 201


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['PUT'])
def actualizar_taller_personal(id_taller_personal):
    data = request.json
    actualizado = TallerPersonalController.actualizar_taller_personal(id_taller_personal, data)
    if actualizado:
        return jsonify({"mensaje": "Taller personal actualizado"})
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404


@taller_personal_bp.route('/<int:id_taller_personal>', methods=['DELETE'])
def eliminar_taller_personal(id_taller_personal):
    eliminado = TallerPersonalController.eliminar_taller_personal(id_taller_personal)
    if eliminado:
        return jsonify({"mensaje": "Taller personal eliminado"})
    return jsonify({"mensaje": "Taller personal no encontrado"}), 404
