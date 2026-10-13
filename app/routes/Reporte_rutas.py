from io import BytesIO

from flask import Blueprint, request, jsonify, send_file
from app.controller.Reporte_Controller import ReporteController
from app.utils.auth import ID_ROL_COORDINADOR, requiere_roles


reporte_bp = Blueprint('reporte_bp', __name__)

TIPO_EXCEL = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


@reporte_bp.before_request
@requiere_roles(ID_ROL_COORDINADOR)
def _restringir_reportes():
    return None


@reporte_bp.route('/<tipo>', methods=['GET'])
def generar_reporte(tipo):
    try:
        contenido, nombre_archivo = ReporteController.generar(tipo, request.args.to_dict())
    except LookupError as error:
        return jsonify({"mensaje": str(error)}), 404
    except ValueError as error:
        return jsonify({"mensaje": str(error)}), 400

    return send_file(
        BytesIO(contenido),
        mimetype=TIPO_EXCEL,
        as_attachment=True,
        download_name=nombre_archivo
    )
