from flask import Flask
from flask_cors import CORS
from app.Config import Config
from flask_mail import Mail

mail = Mail()

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

def crear_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)

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

    return app
