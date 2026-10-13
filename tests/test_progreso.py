"""Progreso automático: aprobar un taller del nivel actual sube al cliente al siguiente nivel."""
from unittest.mock import MagicMock, patch

import pytest

from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Estado_DTO import EstadoDTO
from app.models.dto.Inscripcion_DTO import InscripcionDTO

INSCRIPCION_APROBADA_BASICO = {
    "cliente_cedula": "222", "id_taller": 5, "estado": "Aprobado", "id_tipo_taller": 1,
    "id_progreso": 9, "nivel_actual": 1, "nombre_nivel_actual": "Basico",
}


def _conexion(*filas):
    conexion = MagicMock()
    conexion.cursor.return_value.fetchone.side_effect = list(filas)
    return conexion


def _consultas(conexion):
    return [" ".join(llamada[0][0].split()) for llamada in conexion.cursor.return_value.execute.call_args_list]


class TestAvanzarSiAprobo:

    def test_aprobar_el_nivel_actual_sube_al_siguiente(self):
        conexion = _conexion(INSCRIPCION_APROBADA_BASICO, {"id_tipo_taller": 2, "nombre": "Avanzado"})
        assert ProgresoClienteDAO.avanzar_si_aprobo(3, "7", conexion) == "Avanzado"
        consultas = _consultas(conexion)
        assert any("UPDATE progreso_cliente" in consulta for consulta in consultas)
        assert any("avance_nivel" in consulta for consulta in consultas)
        assert conexion.cursor.return_value.execute.call_args_list[2][0][1] == (2, 9)

    def test_no_hace_commit_propio(self):
        conexion = _conexion(INSCRIPCION_APROBADA_BASICO, {"id_tipo_taller": 2, "nombre": "Avanzado"})
        ProgresoClienteDAO.avanzar_si_aprobo(3, "7", conexion)
        assert not conexion.commit.called

    @pytest.mark.parametrize("cambios", [
        {"estado": "No aprobado"},
        {"estado": "Iniciado"},
        {"id_tipo_taller": 1, "nivel_actual": 2},
        {"id_progreso": None},
    ], ids=["no-aprobado", "iniciado", "taller-de-nivel-anterior", "sin-progreso"])
    def test_casos_sin_cambio_de_nivel(self, cambios):
        conexion = _conexion({**INSCRIPCION_APROBADA_BASICO, **cambios})
        assert ProgresoClienteDAO.avanzar_si_aprobo(3, "7", conexion) is None
        assert not any("UPDATE" in consulta for consulta in _consultas(conexion))

    def test_aprobar_el_ultimo_nivel_no_cambia_nada(self):
        pl = {**INSCRIPCION_APROBADA_BASICO, "id_tipo_taller": 3, "nivel_actual": 3, "nombre_nivel_actual": "PL"}
        conexion = _conexion(pl, None)
        assert ProgresoClienteDAO.avanzar_si_aprobo(3, "7", conexion) is None
        assert not any("UPDATE" in consulta for consulta in _consultas(conexion))

    def test_inscripcion_inexistente(self):
        assert ProgresoClienteDAO.avanzar_si_aprobo(3, "7", _conexion(None)) is None


SERVICIO = "app.services.Inscripcion_Servicio."


@pytest.fixture
def servicio_inscripcion():
    with patch(SERVICIO + "InscripcionDAO") as inscripcion_dao, \
            patch(SERVICIO + "ProgresoClienteDAO") as progreso_dao, \
            patch(SERVICIO + "Db") as db,             patch(SERVICIO + "NotificacionServicio") as notificacion, \
            patch("app.services.Estado_Servicio.EstadoDAO") as estado_dao:
        estado_dao.obtener_por_id.side_effect = lambda id_estado: EstadoDTO(id_estado, "Estado", "inscripcion")
        inscripcion_dao.existe.return_value = False
        inscripcion_dao.obtener_por_id.return_value = InscripcionDTO(3, "222", 5, 3, None)
        inscripcion_dao.actualizar.return_value = True
        inscripcion_dao.crear.return_value = 11
        progreso_dao.avanzar_si_aprobo.return_value = None
        yield {"inscripcion": inscripcion_dao, "progreso": progreso_dao, "conexion": db.obtener_conexion.return_value,
               "notificacion": notificacion}


class TestCoordinadorInscripciones:

    def test_editar_aprobando_informa_el_nuevo_nivel(self, client, servicio_inscripcion, como_coordinador):
        servicio_inscripcion["progreso"].avanzar_si_aprobo.return_value = "Avanzado"
        respuesta = client.put("/api/inscripciones/3", json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 4},
                               headers=como_coordinador)
        assert respuesta.status_code == 200
        assert respuesta.json["nivel_nuevo"] == "Avanzado"

    def test_editar_usa_una_sola_transaccion(self, client, servicio_inscripcion, como_coordinador):
        client.put("/api/inscripciones/3", json={"id_estado": 4}, headers=como_coordinador)
        conexion_actualizar = servicio_inscripcion["inscripcion"].actualizar.call_args[0][2]
        conexion_progreso = servicio_inscripcion["progreso"].avanzar_si_aprobo.call_args[0][2]
        assert conexion_actualizar is conexion_progreso
        assert servicio_inscripcion["progreso"].avanzar_si_aprobo.call_args[0][1] == "3"
        assert servicio_inscripcion["conexion"].commit.called

    def test_editar_notifica_con_el_estado_anterior(self, client, servicio_inscripcion, como_coordinador):
        servicio_inscripcion["progreso"].avanzar_si_aprobo.return_value = "Avanzado"
        client.put("/api/inscripciones/3", json={"id_estado": 4}, headers=como_coordinador)
        servicio_inscripcion["notificacion"].estado_actualizado.assert_called_once_with(3, 3, "Avanzado")

    def test_crear_notifica_la_inscripcion(self, client, servicio_inscripcion, como_coordinador):
        client.post("/api/inscripciones/", json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 3},
                    headers=como_coordinador)
        servicio_inscripcion["notificacion"].inscripcion_creada.assert_called_once_with(11, None)

    def test_editar_inscripcion_inexistente(self, client, servicio_inscripcion, como_coordinador):
        servicio_inscripcion["inscripcion"].actualizar.return_value = False
        assert client.put("/api/inscripciones/99", json={"id_estado": 4}, headers=como_coordinador).status_code == 404
        servicio_inscripcion["progreso"].avanzar_si_aprobo.assert_not_called()
        servicio_inscripcion["notificacion"].estado_actualizado.assert_not_called()

    def test_crear_inscripcion(self, client, servicio_inscripcion, como_coordinador):
        respuesta = client.post("/api/inscripciones/", json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 3},
                                headers=como_coordinador)
        assert respuesta.status_code == 201
        assert respuesta.json == {"mensaje": "Inscripcion creada", "id_inscripcion": 11, "nivel_nuevo": None}

    def test_crear_con_fallo_deshace_la_transaccion(self, client, servicio_inscripcion, como_coordinador):
        servicio_inscripcion["progreso"].avanzar_si_aprobo.side_effect = RuntimeError("fallo de base de datos")
        with pytest.raises(RuntimeError):
            client.post("/api/inscripciones/", json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 4},
                        headers=como_coordinador)
        assert servicio_inscripcion["conexion"].rollback.called
