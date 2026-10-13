"""Configuración común de la suite de pruebas de Lidera360.

Las pruebas NO usan la base de datos ni envían correos reales:
- Las variables de entorno se fijan antes de importar la app, para que el .env local
  (con credenciales reales) no se use.
- Cualquier conexión a MySQL o petición HTTP que no esté simulada hace fallar la prueba.
"""
import os
import sys

# Deben definirse antes de importar `app`, porque Config lee el entorno al importarse
# y load_dotenv() no sobrescribe variables que ya existen.
os.environ["JWT_SECRET_KEY"] = "clave-de-pruebas-" + "x" * 32
os.environ["DB_HOST"] = "base-de-datos-de-pruebas.invalid"
os.environ["DB_USER"] = "pruebas"
os.environ["DB_PASSWORD"] = "pruebas"
os.environ["DB_NAME"] = "pruebas"
os.environ["BREVO_API_KEY"] = "xkeysib-pruebas"
os.environ["BREVO_SENDER_EMAIL"] = "remitente@pruebas.com"
os.environ["FRONTEND_URL"] = "https://frontend.pruebas"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import ExitStack  # noqa: E402
from unittest.mock import patch  # noqa: E402

import pytest  # noqa: E402
from flask_jwt_extended import create_access_token  # noqa: E402

from app import crear_app  # noqa: E402
from app.extensions import limiter  # noqa: E402
from app.utils.auth import (  # noqa: E402
    ID_ROL_CLIENTE,
    ID_ROL_COACH,
    ID_ROL_COORDINADOR,
    ID_ROL_PERSONAL_CAPACITADO,
)


@pytest.fixture(autouse=True)
def sin_recursos_reales(monkeypatch):
    """Falla de inmediato si una prueba intenta usar MySQL o la red sin simularlos."""
    def conexion_prohibida(*args, **kwargs):
        raise AssertionError("La prueba intentó conectarse a MySQL sin simular el DAO")

    def red_prohibida(*args, **kwargs):
        raise AssertionError("La prueba intentó hacer una petición HTTP real")

    monkeypatch.setattr("pymysql.connect", conexion_prohibida)
    monkeypatch.setattr("urllib.request.urlopen", red_prohibida)


DAOS_DE_DESCRIPCIONES = ["ClienteDAO", "EstadoDAO", "InscripcionDAO", "PersonalDAO", "ProgresoClienteDAO",
                         "RolDAO", "TallerDAO", "TallerPersonalDAO", "TipoTallerDAO", "UsuarioDAO"]


@pytest.fixture(autouse=True)
def auditoria_dao():
    with ExitStack() as pila:
        for nombre in DAOS_DE_DESCRIPCIONES:
            pila.enter_context(patch(f"app.utils.descripciones_auditoria.{nombre}"))
        yield pila.enter_context(patch("app.utils.auditoria.AuditoriaDAO"))


@pytest.fixture
def app():
    aplicacion = crear_app()
    aplicacion.config["TESTING"] = True
    limiter.enabled = False
    yield aplicacion
    limiter.enabled = True


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cabeceras(app):
    """Genera cabeceras Authorization con un JWT para el rol indicado."""
    def _cabeceras(id_rol, identidad="1", **claims):
        with app.app_context():
            token = create_access_token(identity=str(identidad), additional_claims={"id_rol": id_rol, **claims})
        return {"Authorization": f"Bearer {token}"}
    return _cabeceras


@pytest.fixture
def como_coach(cabeceras):
    return cabeceras(ID_ROL_COACH, identidad="7", cedula_personal="111")


@pytest.fixture
def como_personal_capacitado(cabeceras):
    return cabeceras(ID_ROL_PERSONAL_CAPACITADO, identidad="6", cedula_personal="1107974839")


@pytest.fixture
def como_cliente(cabeceras):
    return cabeceras(ID_ROL_CLIENTE, identidad="8", cedula_cliente="222")


@pytest.fixture
def como_otro_cliente(cabeceras):
    return cabeceras(ID_ROL_CLIENTE, identidad="9", cedula_cliente="333")


@pytest.fixture
def como_coordinador(cabeceras):
    return cabeceras(ID_ROL_COORDINADOR, identidad="3")
