from flask import Flask, request, jsonify
from flask_cors import CORS
from app.Config import Config

from app.routes.Cliente_rutas import cliente_bp
from app.routes.Usuario_rutas import usuario_bp
from app.routes.Estado_rutas import estado_bp
from app.routes.Rol_rutas import rol_bp
from app.routes.Personal_rutas import personal_bp
from app.routes.Tipo_Taller_rutas import tipo_taller_bp
from app.routes.Taller_rutas import taller_bp
from app.routes.Inscripcion_rutas import inscripcion_bp
from app.routes.Taller_Personal_rutas import taller_personal_bp
from app.routes.Progreso_Cliente_rutas import progreso_cliente_bp
from app.routes.Auditoria_rutas import auditoria_bp
from app.controller.Usuario_Controller import UsuarioController

def crear_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    app.register_blueprint(cliente_bp, url_prefix='/api/clientes')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(estado_bp, url_prefix='/api/estados')
    app.register_blueprint(rol_bp, url_prefix='/api/roles')
    app.register_blueprint(personal_bp, url_prefix='/api/personal')
    app.register_blueprint(tipo_taller_bp, url_prefix='/api/tipos-taller')
    app.register_blueprint(taller_bp, url_prefix='/api/talleres')
    app.register_blueprint(inscripcion_bp, url_prefix='/api/inscripciones')
    app.register_blueprint(taller_personal_bp, url_prefix='/api/taller-personal')
    app.register_blueprint(progreso_cliente_bp, url_prefix='/api/progresos-clientes')
    app.register_blueprint(auditoria_bp, url_prefix='/api/auditorias')

    @app.route('/usuario/create_admin', methods=['POST'])
    def usuario_create_admin_alias():
        data = request.get_json(silent=True) or {}
        campos_requeridos = ['cedula_personal', 'username', 'password']
        campos_faltantes = [c for c in campos_requeridos if c not in data or data[c] in (None, '')]
        if campos_faltantes:
            return jsonify({"mensaje": "Faltan campos obligatorios", "campos": campos_faltantes}), 400

        try:
            resultado = UsuarioController.crear_admin_desde_personal(data)
            return jsonify({"mensaje": "Admin creado correctamente", **resultado}), 201
        except ValueError as error:
            return jsonify({"mensaje": str(error)}), 409
        except Exception as e:
            return jsonify({"mensaje": "Error creando admin", "error": str(e)}), 500

    return app
