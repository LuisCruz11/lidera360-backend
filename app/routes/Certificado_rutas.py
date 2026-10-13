from flask import Blueprint, jsonify
from app.controller.Certificado_Controller import CertificadoController
from app.extensions import limiter


certificado_bp = Blueprint('certificado_bp', __name__)

# Ruta pública (registrada en RUTAS_PUBLICAS_PREFIJO): permite a terceros validar un certificado por su código.
@certificado_bp.route('/verificar/<codigo>', methods=['GET'])
@limiter.limit("30 per minute")
def verificar_certificado(codigo):
    resultado = CertificadoController.verificar(codigo)
    return jsonify(resultado), 200 if "codigo" in resultado else 404
