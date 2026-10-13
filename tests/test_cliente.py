"""Portal del cliente: cancelar inscripción y editar datos de contacto."""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dto.Cliente_DTO import ClienteDTO

EN_5_DIAS = date.today() + timedelta(days=5)
AYER = date.today() - timedelta(days=1)


class TestPuedeCancelar:

    @pytest.mark.parametrize("fila, esperado", [
        ({"id_inscripcion": 1, "estado_inscripcion": "Iniciado", "fecha_inicio": EN_5_DIAS}, True),
        ({"id_inscripcion": 1, "estado_inscripcion": "Iniciado", "fecha_inicio": AYER}, False),
        ({"id_inscripcion": 1, "estado_inscripcion": "Aprobado", "fecha_inicio": EN_5_DIAS}, False),
        ({"id_inscripcion": 1, "estado_inscripcion": "Iniciado", "fecha_inicio": None}, False),
        ({"id_inscripcion": None, "estado_inscripcion": None, "fecha_inicio": EN_5_DIAS}, False),
    ], ids=["iniciado-futuro", "ya-empezo", "ya-aprobado", "sin-fecha", "taller-disponible"])
    def test_reglas(self, fila, esperado):
        assert ClienteDAO._puede_cancelar(fila) is esperado


@pytest.fixture
def conexion():
    """Conexión simulada para los métodos de ClienteDAO que abren su propia conexión."""
    with patch("app.models.dao.Cliente_DAO.Db") as db:
        conexion = MagicMock()
        db.obtener_conexion.return_value = conexion
        yield conexion


def _inscripcion(fecha_inicio, estado="Iniciado"):
    return {"id_inscripcion": 3, "id_taller": 5, "taller_nombre": "Taller", "fecha_inicio": fecha_inicio,
            "estado_inscripcion": estado}


class TestCancelarInscripcion:

    def test_cancela_y_registra_en_auditoria(self, client, conexion, como_cliente):
        conexion.cursor.return_value.fetchone.return_value = _inscripcion(EN_5_DIAS)
        with patch("app.services.Cliente_Servicio.NotificacionServicio"):
            respuesta = client.delete("/api/clientes/222/inscripciones/3", headers=como_cliente)
        consultas = " ".join(llamada[0][0] for llamada in conexion.cursor.return_value.execute.call_args_list)
        assert respuesta.status_code == 200
        assert "DELETE FROM inscripcion" in consultas
        assert "cancelacion" in consultas
        assert conexion.commit.called

    def test_no_cancela_si_el_taller_ya_empezo(self, client, conexion, como_cliente):
        conexion.cursor.return_value.fetchone.return_value = _inscripcion(AYER)
        with patch("app.services.Cliente_Servicio.NotificacionServicio"):
            respuesta = client.delete("/api/clientes/222/inscripciones/3", headers=como_cliente)
        assert respuesta.status_code == 400
        assert conexion.rollback.called

    def test_inscripcion_inexistente(self, client, conexion, como_cliente):
        conexion.cursor.return_value.fetchone.return_value = None
        with patch("app.services.Cliente_Servicio.NotificacionServicio"):
            assert client.delete("/api/clientes/222/inscripciones/3", headers=como_cliente).status_code == 404

    def test_no_puede_cancelar_la_inscripcion_de_otro_cliente(self, client, como_otro_cliente):
        assert client.delete("/api/clientes/222/inscripciones/3", headers=como_otro_cliente).status_code == 403


@pytest.fixture
def cliente_dao():
    with patch("app.services.Cliente_Servicio.ClienteDAO") as dao:
        dao.obtener_por_cedula.return_value = ClienteDTO("222", "Ana", "Pérez", "ana@correo.co", "3001234567", "F", 20, 1)
        dao.obtener_por_correo.return_value = None
        yield dao


class TestEditarContacto:

    def test_actualiza_correo_y_telefono(self, client, cliente_dao, como_cliente):
        respuesta = client.put("/api/clientes/222/perfil", json={"correo": "nuevo@correo.co", "telefono": "3109998877"},
                               headers=como_cliente)
        assert respuesta.status_code == 200
        cliente_dao.actualizar_contacto.assert_called_once_with("222", "nuevo@correo.co", "3109998877")

    @pytest.mark.parametrize("datos", [
        {"correo": "correo-invalido", "telefono": "3109998877"},
        {"correo": "ana@correo.co", "telefono": "12"},
        {"correo": "", "telefono": "3109998877"},
    ], ids=["correo-invalido", "telefono-corto", "correo-vacio"])
    def test_valida_los_datos(self, client, cliente_dao, como_cliente, datos):
        assert client.put("/api/clientes/222/perfil", json=datos, headers=como_cliente).status_code == 400
        cliente_dao.actualizar_contacto.assert_not_called()

    def test_no_permite_un_correo_de_otro_cliente(self, client, cliente_dao, como_cliente):
        cliente_dao.obtener_por_correo.return_value = ClienteDTO("999", "Otro", "Cliente", "otro@correo.co", "1", "M", 30, 1)
        respuesta = client.put("/api/clientes/222/perfil", json={"correo": "otro@correo.co", "telefono": "3109998877"},
                               headers=como_cliente)
        assert respuesta.json["mensaje"] == "El correo ya esta registrado"

    def test_no_puede_editar_el_perfil_de_otro_cliente(self, client, como_otro_cliente):
        assert client.put("/api/clientes/222/perfil", json={}, headers=como_otro_cliente).status_code == 403
