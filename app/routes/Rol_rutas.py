from flask import Blueprint, request, jsonify
from app.controller.Rol_Controller import RolController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles
from app.utils.auditoria import auditar
import app.utils.descripciones_auditoria as da
from app.models.dao.Rol_DAO import RolDAO


rol_bp = Blueprint('rol_bp', __name__)


@rol_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_rol():
    return None


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
@auditar("roles", "crear", da.catalogo_creado("rol"))
def crear_rol():
    data = request.json
    id_rol = RolController.crear_rol(data)
    return jsonify({"mensaje": "Rol creado", "id_rol": id_rol}), 201


@rol_bp.route('/<int:id_rol>', methods=['PUT'])
@auditar("roles", "actualizar", da.catalogo_actualizado("rol", "id_rol"))
def actualizar_rol(id_rol):
    data = request.json
    actualizado = RolController.actualizar_rol(id_rol, data)
    if actualizado:
        return jsonify({"mensaje": "Rol actualizado"})
    return jsonify({"mensaje": "Rol no encontrado"}), 404


@rol_bp.route('/<int:id_rol>', methods=['DELETE'])
@auditar("roles", "eliminar", da.catalogo_eliminado("rol", "id_rol"), antes=da.antes_de_eliminar_catalogo(RolDAO, "id_rol"))
def eliminar_rol(id_rol):
    eliminado = RolController.eliminar_rol(id_rol)
    if eliminado:
        return jsonify({"mensaje": "Rol eliminado"})
    return jsonify({"mensaje": "Rol no encontrado"}), 404
