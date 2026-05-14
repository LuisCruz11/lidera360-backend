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
    data = request.get_json(silent=True) or {}
    campos_requeridos = ['cedula', 'nombres', 'apellidos', 'correo', 'telefono', 'id_rol']
    campos_faltantes = [
        campo for campo in campos_requeridos
        if campo not in data or data[campo] in (None, '')
    ]

    if campos_faltantes:
        return jsonify({
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:
        resultado = PersonalController.crear_persona(data)
        return jsonify({"mensaje": "Personal creado", **resultado}), 201
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 409


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
