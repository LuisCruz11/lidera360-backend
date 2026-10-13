"""Recuperación de contraseña con enlace firmado de un solo uso."""
import time
from unittest.mock import patch

import bcrypt
import pytest

from app.models.dto.Usuario_DTO import UsuarioDTO
from app.utils.recuperacion_password import generar_token

SERVICIO = "app.services.Usuario_servicio."
HASH_ACTUAL = bcrypt.hashpw(b"Vieja123!", bcrypt.gensalt()).decode()
USUARIO = UsuarioDTO(5, "PruebaCliente", HASH_ACTUAL, 4, None, 1, "222")


@pytest.fixture
def usuario_dao():
    with patch(SERVICIO + "UsuarioDAO") as dao:
        dao.obtener_por_correo.return_value = (USUARIO, "Ana", "ana@correo.co")
        dao.obtener_por_id.return_value = USUARIO
        yield dao


@pytest.fixture
def enviar_correo():
    with patch(SERVICIO + "enviar_correo_recuperacion") as enviar:
        yield enviar


@pytest.fixture
def token(app):
    with app.app_context():
        return generar_token(USUARIO.id_usuario, HASH_ACTUAL)


def _restablecer(client, token, password="Nueva123!"):
    return client.post("/api/usuarios/restablecer-password", json={"token": token, "password_nueva": password})


class TestSolicitar:

    def test_es_publica_y_envia_el_enlace(self, client, usuario_dao, enviar_correo):
        respuesta = client.post("/api/usuarios/recuperar-password", json={"correo": "ana@correo.co"})
        destinatario, nombre, enlace = enviar_correo.call_args[0]
        assert respuesta.status_code == 200
        assert (destinatario, nombre) == ("ana@correo.co", "Ana")
        assert enlace.startswith("https://frontend.pruebas/?restablecer=")

    def test_no_revela_si_el_correo_existe(self, client, usuario_dao, enviar_correo):
        existente = client.post("/api/usuarios/recuperar-password", json={"correo": "ana@correo.co"})
        usuario_dao.obtener_por_correo.return_value = None
        enviar_correo.reset_mock()
        inexistente = client.post("/api/usuarios/recuperar-password", json={"correo": "nadie@correo.co"})
        assert (inexistente.status_code, inexistente.json) == (existente.status_code, existente.json)
        enviar_correo.assert_not_called()

    def test_un_fallo_del_correo_no_se_revela(self, client, usuario_dao, enviar_correo):
        enviar_correo.side_effect = RuntimeError("Brevo caído")
        assert client.post("/api/usuarios/recuperar-password", json={"correo": "ana@correo.co"}).status_code == 200

    def test_correo_con_formato_invalido(self, client, usuario_dao, enviar_correo):
        assert client.post("/api/usuarios/recuperar-password", json={"correo": "x"}).status_code == 400


class TestRestablecer:

    def test_restablece_con_un_enlace_valido(self, client, usuario_dao, token):
        respuesta = _restablecer(client, token)
        assert respuesta.status_code == 200
        id_usuario, nuevo_hash = usuario_dao.actualizar_password.call_args[0]
        assert id_usuario == 5
        assert bcrypt.checkpw(b"Nueva123!", nuevo_hash.encode())

    def test_el_enlace_solo_sirve_una_vez(self, client, usuario_dao, token):
        _restablecer(client, token)
        nuevo_hash = usuario_dao.actualizar_password.call_args[0][1]
        usuario_dao.obtener_por_id.return_value = UsuarioDTO(5, "PruebaCliente", nuevo_hash, 4, None, 1, "222")
        respuesta = _restablecer(client, token, "Otra1234!")
        assert respuesta.status_code == 400
        assert "ya fue usado" in respuesta.json["mensaje"]

    def test_el_enlace_vence_a_los_30_minutos(self, client, usuario_dao, token):
        with patch("itsdangerous.timed.time.time", return_value=time.time() + 31 * 60):
            respuesta = _restablecer(client, token)
        assert respuesta.json["mensaje"] == "El enlace de recuperación venció. Solicita uno nuevo."

    def test_enlace_alterado(self, client, usuario_dao, token):
        respuesta = _restablecer(client, token[:-3] + "abc")
        assert respuesta.json["mensaje"] == "El enlace de recuperación no es válido."

    def test_usuario_inactivo(self, client, usuario_dao, token):
        usuario_dao.obtener_por_id.return_value = UsuarioDTO(5, "PruebaCliente", HASH_ACTUAL, 4, None, 0, "222")
        assert _restablecer(client, token).status_code == 400

    def test_exige_una_contrasena_segura(self, client, usuario_dao, token):
        respuesta = _restablecer(client, token, "abc")
        assert respuesta.status_code == 400
        usuario_dao.actualizar_password.assert_not_called()

    def test_sin_token(self, client, usuario_dao):
        respuesta = client.post("/api/usuarios/restablecer-password", json={"password_nueva": "Nueva123!"})
        assert respuesta.status_code == 400
