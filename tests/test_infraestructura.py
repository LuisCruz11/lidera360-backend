"""Envío de correos por Brevo y configuración de la conexión a MySQL."""
import json
from unittest.mock import MagicMock, patch

import pytest
from pymysql.constants import CLIENT

from app.database.Db import Db
from app.utils import email_service


@pytest.fixture
def urlopen():
    with patch("urllib.request.urlopen") as abrir:
        abrir.return_value.__enter__.return_value.read.return_value = b'{"messageId": "1"}'
        yield abrir


class TestCorreo:

    def test_envia_por_brevo_con_el_remitente_configurado(self, app, urlopen):
        with app.app_context():
            email_service.enviar_correo_recuperacion("ana@correo.co", "Ana", "https://enlace")
        peticion = urlopen.call_args[0][0]
        cuerpo = json.loads(peticion.data)
        assert peticion.full_url == "https://api.brevo.com/v3/smtp/email"
        assert peticion.get_header("Api-key") == "xkeysib-pruebas"
        assert cuerpo["sender"] == {"name": "Lidera360", "email": "remitente@pruebas.com"}
        assert cuerpo["to"] == [{"email": "ana@correo.co"}]
        assert "https://enlace" in cuerpo["htmlContent"]

    def test_envia_un_user_agent_propio(self, app, urlopen):
        # Cloudflare bloquea el User-Agent por defecto de urllib con el error 1010.
        with app.app_context():
            email_service.enviar_correo_registro("ana@correo.co", "Ana")
        assert urlopen.call_args[0][0].get_header("User-agent") == "Lidera360/1.0"

    def test_usa_un_tiempo_maximo_de_espera(self, app, urlopen):
        with app.app_context():
            email_service.enviar_correo_registro("ana@correo.co", "Ana")
        assert urlopen.call_args.kwargs["timeout"] == 10

    @pytest.mark.parametrize("variable", ["BREVO_API_KEY", "BREVO_SENDER_EMAIL"])
    def test_falla_si_falta_configuracion(self, app, urlopen, variable):
        app.config[variable] = None
        with app.app_context(), pytest.raises(ValueError, match=variable):
            email_service.enviar_correo_registro("ana@correo.co", "Ana")
        urlopen.assert_not_called()


class TestConexionMySQL:

    def test_cuenta_filas_encontradas_en_los_update(self):
        # Sin FOUND_ROWS, guardar un registro sin cambios se reportaba como "no encontrado".
        with patch("pymysql.connect", MagicMock()) as conectar:
            Db.obtener_conexion()
        assert conectar.call_args.kwargs["client_flag"] & CLIENT.FOUND_ROWS
