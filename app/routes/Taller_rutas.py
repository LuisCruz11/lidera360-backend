from flask import Blueprint, request, jsonify
from app.controller.Taller_Controller import TallerController


taller_bp = Blueprint('taller_bp', __name__)


@taller_bp.route('/', methods=['GET'])
def obtener_talleres():
    return jsonify(TallerController.obtener_talleres())


@taller_bp.route('/<int:id_taller>', methods=['GET'])
def obtener_taller(id_taller):
    taller = TallerController.obtener_taller(id_taller)
    if taller:
        return jsonify(taller)
    return jsonify({"mensaje": "Taller no encontrado"}), 404


@taller_bp.route('/', methods=['POST'])
def crear_taller():
    data = request.json
    id_taller = TallerController.crear_taller(data)
    return jsonify({"mensaje": "Taller creado", "id_taller": id_taller}), 201


@taller_bp.route('/<int:id_taller>', methods=['PUT'])
def actualizar_taller(id_taller):
    data = request.json
    actualizado = TallerController.actualizar_taller(id_taller, data)
    if actualizado:
        return jsonify({"mensaje": "Taller actualizado"})
    return jsonify({"mensaje": "Taller no encontrado"}), 404


@taller_bp.route('/<int:id_taller>', methods=['DELETE'])
def eliminar_taller(id_taller):
    eliminado = TallerController.eliminar_taller(id_taller)
    if eliminado:
        return jsonify({"mensaje": "Taller eliminado"})
    return jsonify({"mensaje": "Taller no encontrado"}), 404
