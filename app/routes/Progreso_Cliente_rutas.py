from flask import Blueprint, request, jsonify
from app.controller.Progreso_Cliente_Controller import ProgresoClienteController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles
from app.utils.auditoria import auditar
import app.utils.descripciones_auditoria as da


progreso_cliente_bp = Blueprint('progreso_cliente_bp', __name__)


@progreso_cliente_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_progreso_cliente():
    return None


@progreso_cliente_bp.route('/', methods=['GET'])
def obtener_progresos():
    return jsonify(ProgresoClienteController.obtener_progresos())


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['GET'])
def obtener_progreso(id_progreso):
    progreso = ProgresoClienteController.obtener_progreso(id_progreso)
    if progreso:
        return jsonify(progreso)
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/cliente/<cliente_cedula>', methods=['GET'])
def obtener_progreso_por_cliente(cliente_cedula):
    progreso = ProgresoClienteController.obtener_progreso_por_cliente(cliente_cedula)
    if progreso:
        return jsonify(progreso)
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/', methods=['POST'])
@auditar("progreso_cliente", "crear", da.progreso_guardado)
def crear_progreso():
    data = request.json
    id_progreso = ProgresoClienteController.crear_progreso(data)
    return jsonify({"mensaje": "Progreso creado", "id_progreso": id_progreso}), 201


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['PUT'])
@auditar("progreso_cliente", "actualizar", da.progreso_guardado)
def actualizar_progreso(id_progreso):
    data = request.json
    actualizado = ProgresoClienteController.actualizar_progreso(id_progreso, data)
    if actualizado:
        return jsonify({"mensaje": "Progreso actualizado"})
    return jsonify({"mensaje": "Progreso no encontrado"}), 404


@progreso_cliente_bp.route('/<int:id_progreso>', methods=['DELETE'])
@auditar("progreso_cliente", "eliminar", da.progreso_eliminado, antes=da.antes_de_eliminar_progreso)
def eliminar_progreso(id_progreso):
    eliminado = ProgresoClienteController.eliminar_progreso(id_progreso)
    if eliminado:
        return jsonify({"mensaje": "Progreso eliminado"})
    return jsonify({"mensaje": "Progreso no encontrado"}), 404
