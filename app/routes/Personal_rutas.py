from flask import Blueprint, request, jsonify
from app.controller.Personal_Controller import PersonalController


personal_bp = Blueprint('personal_bp', __name__)


@personal_bp.route('/', methods=['GET'])
def obtener_personal():
    return jsonify(PersonalController.obtener_personal())


@personal_bp.route('/<cedula>', methods=['GET'])
def obtener_persona(cedula):
    persona = PersonalController.obtener_persona(cedula)
    if persona:
        return jsonify(persona)
    return jsonify({"mensaje": "Personal no encontrado"}), 404


@personal_bp.route('/', methods=['POST'])
def crear_persona():
    data = request.json
    PersonalController.crear_persona(data)
    return jsonify({"mensaje": "Personal creado"}), 201


@personal_bp.route('/<cedula>', methods=['PUT'])
def actualizar_persona(cedula):
    data = request.json
    actualizado = PersonalController.actualizar_persona(cedula, data)
    if actualizado:
        return jsonify({"mensaje": "Personal actualizado"})
    return jsonify({"mensaje": "Personal no encontrado"}), 404


@personal_bp.route('/<cedula>', methods=['DELETE'])
def eliminar_persona(cedula):
    eliminado = PersonalController.eliminar_persona(cedula)
    if eliminado:
        return jsonify({"mensaje": "Personal eliminado"})
    return jsonify({"mensaje": "Personal no encontrado"}), 404
