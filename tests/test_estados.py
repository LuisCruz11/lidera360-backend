"""Estados separados por uso: cliente, taller e inscripción."""
from unittest.mock import MagicMock, patch

import pytest

from app.models.dao.Estado_DAO import EstadoDAO
from app.models.dto.Estado_DTO import EstadoDTO
from app.services.Estado_Servicio import EstadoServicio

ESTADOS = {
    1: EstadoDTO(1, "Activo", "cliente,taller"),
    3: EstadoDTO(3, "Iniciado", "inscripcion"),
    4: EstadoDTO(4, "Aprobado", "inscripcion"),
    7: EstadoDTO(7, "Planificado", "taller"),
}


@pytest.fixture
def estado_dao():
    with patch("app.services.Estado_Servicio.EstadoDAO") as dao:
        dao.obtener_por_id.side_effect = lambda id_estado: ESTADOS.get(int(id_estado))
        dao.obtener_todos.return_value = list(ESTADOS.values())
        dao.crear.return_value = 9
        dao.actualizar.return_value = True
        yield dao


class TestEstadoDTO:

    @pytest.mark.parametrize("valor, esperado", [
        ("cliente,taller", ["cliente", "taller"]),
        ({"inscripcion", "cliente"}, ["cliente", "inscripcion"]),
        (None, ["cliente", "taller", "inscripcion"]),
        ("taller, inscripcion", ["taller", "inscripcion"]),
    ], ids=["texto", "set-de-mysql", "sin-columna", "con-espacios"])
    def test_interpreta_aplica_a(self, valor, esperado):
        assert EstadoDTO(1, "X", valor).aplica_a == esperado


class TestValidacion:

    @pytest.mark.parametrize("id_estado, ambito", [(1, "cliente"), (1, "taller"), (7, "taller"), (4, "inscripcion")])
    def test_estados_validos(self, estado_dao, id_estado, ambito):
        assert EstadoServicio.validar_estado_para(id_estado, ambito).id_estado == id_estado

    @pytest.mark.parametrize("id_estado, ambito, mensaje", [
        (4, "cliente", "El estado Aprobado no se puede asignar a un cliente"),
        (3, "taller", "El estado Iniciado no se puede asignar a un taller"),
        (1, "inscripcion", "El estado Activo no se puede asignar a una inscripción"),
        (99, "cliente", "El estado seleccionado no existe"),
        (None, "taller", "El estado seleccionado no existe"),
    ], ids=["cliente-aprobado", "taller-iniciado", "inscripcion-activo", "inexistente", "vacio"])
    def test_estados_invalidos(self, estado_dao, id_estado, ambito, mensaje):
        with pytest.raises(ValueError, match=mensaje):
            EstadoServicio.validar_estado_para(id_estado, ambito)


class TestRutaEstados:

    def test_filtra_por_uso(self, client, estado_dao, como_coordinador):
        respuesta = client.get("/api/estados/?aplica_a=taller", headers=como_coordinador)
        assert respuesta.status_code == 200
        estado_dao.obtener_todos.assert_called_once_with("taller")
        assert respuesta.json[0]["aplica_a"] == ["cliente", "taller"]

    def test_sin_filtro_devuelve_todos(self, client, estado_dao, como_coordinador):
        client.get("/api/estados/", headers=como_coordinador)
        estado_dao.obtener_todos.assert_called_once_with(None)

    def test_filtro_invalido(self, client, estado_dao, como_coordinador):
        assert client.get("/api/estados/?aplica_a=planeta", headers=como_coordinador).status_code == 400

    def test_crear_estado_con_su_uso(self, client, estado_dao, como_coordinador):
        respuesta = client.post("/api/estados/", json={"nombre": "Suspendido", "aplica_a": ["cliente"]},
                                headers=como_coordinador)
        assert respuesta.status_code == 201
        assert estado_dao.crear.call_args[0][0].aplica_a == ["cliente"]

    def test_crear_estado_sin_uso_aplica_a_todo(self, client, estado_dao, como_coordinador):
        client.post("/api/estados/", json={"nombre": "Otro"}, headers=como_coordinador)
        assert estado_dao.crear.call_args[0][0].aplica_a == ["cliente", "taller", "inscripcion"]

    def test_crear_estado_con_uso_invalido(self, client, estado_dao, como_coordinador):
        respuesta = client.post("/api/estados/", json={"nombre": "X", "aplica_a": ["planeta"]}, headers=como_coordinador)
        assert respuesta.status_code == 400
        estado_dao.crear.assert_not_called()


class TestConsultaDAO:

    def test_filtra_con_find_in_set(self):
        with patch("app.models.dao.Estado_DAO.Db") as db:
            conexion = MagicMock()
            conexion.cursor.return_value.fetchall.return_value = [(7, "Planificado", "taller")]
            db.obtener_conexion.return_value = conexion
            estados = EstadoDAO.obtener_todos("taller")
        sql, parametros = conexion.cursor.return_value.execute.call_args[0]
        assert "FIND_IN_SET(%s, aplica_a)" in sql
        assert parametros == ("taller",)
        assert estados[0].aplica_a == ["taller"]


class TestGuardadoRechazaEstadosAjenos:

    def test_cliente_con_estado_de_inscripcion(self, client, estado_dao, como_coordinador):
        with patch("app.services.Cliente_Servicio.ClienteDAO") as cliente_dao:
            respuesta = client.put("/api/clientes/222", headers=como_coordinador, json={
                "nombres": "Ana", "apellidos": "Pérez", "sexo": "F", "edad": 20, "id_estado": 4,
            })
        assert respuesta.status_code == 400
        assert respuesta.json["mensaje"] == "El estado Aprobado no se puede asignar a un cliente"
        cliente_dao.actualizar.assert_not_called()

    def test_taller_con_estado_de_inscripcion(self, client, estado_dao, como_coordinador):
        with patch("app.services.Taller_Servicio.TallerDAO") as taller_dao:
            respuesta = client.post("/api/talleres/", headers=como_coordinador, json={
                "nombre": "T", "id_tipo_taller": 1, "fecha_inicio": "2026-10-16", "fecha_fin": "2026-10-18", "id_estado": 3,
            })
        assert respuesta.status_code == 400
        taller_dao.crear.assert_not_called()

    def test_inscripcion_con_estado_de_cliente(self, client, estado_dao, como_coordinador):
        with patch("app.services.Inscripcion_Servicio.InscripcionDAO") as inscripcion_dao:
            inscripcion_dao.existe.return_value = False
            respuesta = client.post("/api/inscripciones/", headers=como_coordinador,
                                    json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 1})
        assert respuesta.json["mensaje"] == "El estado Activo no se puede asignar a una inscripción"
        inscripcion_dao.crear.assert_not_called()

    def test_editar_inscripcion_con_estado_de_taller(self, client, estado_dao, como_coordinador):
        with patch("app.services.Inscripcion_Servicio.InscripcionDAO") as inscripcion_dao:
            respuesta = client.put("/api/inscripciones/3", headers=como_coordinador, json={"id_estado": 7})
        assert respuesta.status_code == 400
        inscripcion_dao.actualizar.assert_not_called()
