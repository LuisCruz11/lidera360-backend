from flask import Blueprint, request, jsonify
from app.controller.Inscripcion_Controller import InscripcionController


inscripcion_bp = Blueprint('inscripcion_bp', __name__)


@inscripcion_bp.route('/', methods=['GET'])
def obtener_inscripciones():
    return jsonify(InscripcionController.obtener_inscripciones())


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['GET'])
def obtener_inscripcion(id_inscripcion):
    inscripcion = InscripcionController.obtener_inscripcion(id_inscripcion)
    if inscripcion:
        return jsonify(inscripcion)
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404


@inscripcion_bp.route('/', methods=['POST'])
def crear_inscripcion():
    data = request.json
    id_inscripcion = InscripcionController.crear_inscripcion(data)
    return jsonify({"mensaje": "Inscripcion creada", "id_inscripcion": id_inscripcion}), 201


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['PUT'])
def actualizar_inscripcion(id_inscripcion):
    data = request.json
    actualizado = InscripcionController.actualizar_inscripcion(id_inscripcion, data)
    if actualizado:
        return jsonify({"mensaje": "Inscripcion actualizada"})
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404


@inscripcion_bp.route('/<int:id_inscripcion>', methods=['DELETE'])
def eliminar_inscripcion(id_inscripcion):
    eliminado = InscripcionController.eliminar_inscripcion(id_inscripcion)
    if eliminado:
        return jsonify({"mensaje": "Inscripcion eliminada"})
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404
