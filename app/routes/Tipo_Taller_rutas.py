from flask import Blueprint, request, jsonify
from app.controller.Tipo_Taller_Controller import TipoTallerController


tipo_taller_bp = Blueprint('tipo_taller_bp', __name__)


@tipo_taller_bp.route('/', methods=['GET'])
def obtener_tipos_taller():
    return jsonify(TipoTallerController.obtener_tipos_taller())


@tipo_taller_bp.route('/<int:id_tipo_taller>', methods=['GET'])
def obtener_tipo_taller(id_tipo_taller):
    tipo = TipoTallerController.obtener_tipo_taller(id_tipo_taller)
    if tipo:
        return jsonify(tipo)
    return jsonify({"mensaje": "Tipo de taller no encontrado"}), 404


@tipo_taller_bp.route('/', methods=['POST'])
def crear_tipo_taller():
    data = request.json
    id_tipo_taller = TipoTallerController.crear_tipo_taller(data)
    return jsonify({"mensaje": "Tipo de taller creado", "id_tipo_taller": id_tipo_taller}), 201


@tipo_taller_bp.route('/<int:id_tipo_taller>', methods=['PUT'])
def actualizar_tipo_taller(id_tipo_taller):
    data = request.json
    actualizado = TipoTallerController.actualizar_tipo_taller(id_tipo_taller, data)
    if actualizado:
        return jsonify({"mensaje": "Tipo de taller actualizado"})
    return jsonify({"mensaje": "Tipo de taller no encontrado"}), 404


@tipo_taller_bp.route('/<int:id_tipo_taller>', methods=['DELETE'])
def eliminar_tipo_taller(id_tipo_taller):
    eliminado = TipoTallerController.eliminar_tipo_taller(id_tipo_taller)
    if eliminado:
        return jsonify({"mensaje": "Tipo de taller eliminado"})
    return jsonify({"mensaje": "Tipo de taller no encontrado"}), 404
