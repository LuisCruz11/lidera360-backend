"""Módulo del Coach: talleres asignados, participantes, actividades y evaluación."""
from unittest.mock import MagicMock, patch

import pytest

from app.models.dto.Estado_DTO import EstadoDTO
from app.models.dto.Inscripcion_DTO import InscripcionDTO
from app.models.dto.Taller_DTO import TallerDTO

SERVICIO = "app.services.Coach_Servicio."
TALLER = TallerDTO(5, "Taller de prueba", 1, None, None, 1)


@pytest.fixture
def daos():
    """Simula los DAO del servicio del coach (la validación de asignación comparte TallerDAO)."""
    taller_dao = MagicMock()
    taller_dao.obtener_por_id.return_value = TALLER
    taller_dao.tiene_personal_asignado.return_value = True
    taller_dao.obtener_por_personal.return_value = [{"id_taller": 5}]
    taller_dao.obtener_detalle.return_value = {"taller": {}, "clientes_inscritos": [], "notas": []}

    with patch("app.services.Asignacion_Taller.TallerDAO", taller_dao), \
            patch(SERVICIO + "TallerDAO", taller_dao), \
            patch(SERVICIO + "InscripcionDAO") as inscripcion_dao, \
            patch("app.services.Estado_Servicio.EstadoDAO") as estado_dao, \
            patch(SERVICIO + "AuditoriaDAO") as auditoria_dao, \
            patch(SERVICIO + "ProgresoClienteDAO") as progreso_dao, \
            patch(SERVICIO + "Db") as db,             patch(SERVICIO + "NotificacionServicio") as notificacion:
        inscripcion_dao.obtener_por_id.return_value = InscripcionDTO(3, "222", 5, 1, None)
        estado_dao.obtener_por_id.return_value = EstadoDTO(4, "Aprobado", "inscripcion")
        progreso_dao.avanzar_si_aprobo.return_value = None
        auditoria_dao.crear.return_value = 99
        yield {
            "taller": taller_dao,
            "inscripcion": inscripcion_dao,
            "estado": estado_dao,
            "auditoria": auditoria_dao,
            "progreso": progreso_dao,
            "conexion": db.obtener_conexion.return_value,
            "notificacion": notificacion,
        }


class TestPermisos:

    def test_sin_token_responde_401(self, client):
        assert client.get("/api/coach/talleres").status_code == 401

    def test_un_cliente_no_puede_entrar(self, client, daos, como_cliente):
        assert client.get("/api/coach/talleres", headers=como_cliente).status_code == 403

    def test_coach_sin_cedula_de_personal(self, client, daos, cabeceras):
        respuesta = client.get("/api/coach/talleres", headers=cabeceras(2, cedula_personal=None))
        assert respuesta.status_code == 403

    def test_taller_no_asignado_responde_403(self, client, daos, como_coach):
        daos["taller"].tiene_personal_asignado.return_value = False
        assert client.get("/api/coach/talleres/5", headers=como_coach).status_code == 403

    def test_taller_inexistente_responde_404(self, client, daos, como_coach):
        daos["taller"].obtener_por_id.return_value = None
        assert client.get("/api/coach/talleres/77", headers=como_coach).status_code == 404

    def test_el_coach_puede_consultar_estados(self, client, como_coach):
        with patch("app.routes.Estado_rutas.EstadoController") as controlador:
            controlador.obtener_estados.return_value = []
            assert client.get("/api/estados/", headers=como_coach).status_code == 200


class TestTalleres:

    def test_lista_solo_los_talleres_donde_es_coach(self, client, daos, como_coach):
        respuesta = client.get("/api/coach/talleres", headers=como_coach)
        assert respuesta.status_code == 200
        daos["taller"].obtener_por_personal.assert_called_once_with("111", "coach")

    def test_detalle_del_taller_asignado(self, client, daos, como_coach):
        assert client.get("/api/coach/talleres/5", headers=como_coach).status_code == 200


class TestActividades:

    def test_registrar_actividad(self, client, daos, como_coach):
        respuesta = client.post("/api/coach/talleres/5/actividades", json={"descripcion": "Dinámica"}, headers=como_coach)
        assert respuesta.status_code == 201
        assert respuesta.json["id_auditoria"] == 99
        assert daos["auditoria"].crear.call_args[0][0].accion == "actividad"

    def test_actividad_sin_descripcion(self, client, daos, como_coach):
        respuesta = client.post("/api/coach/talleres/5/actividades", json={"descripcion": "  "}, headers=como_coach)
        assert respuesta.status_code == 400


class TestEvaluacion:

    def test_evaluar_actualiza_estado_y_registra_en_bitacora(self, client, daos, como_coach):
        respuesta = client.put(
            "/api/coach/inscripciones/3/evaluacion",
            json={"id_estado": 4, "observacion": "Excelente"},
            headers=como_coach,
        )
        assert respuesta.status_code == 200
        assert daos["inscripcion"].actualizar_estado.call_args[0][:2] == (3, 4)
        descripcion = daos["auditoria"].crear.call_args[0][0].descripcion
        assert "Aprobado" in descripcion and "Excelente" in descripcion
        assert daos["conexion"].commit.called

    def test_evaluar_informa_el_avance_de_nivel(self, client, daos, como_coach):
        daos["progreso"].avanzar_si_aprobo.return_value = "Avanzado"
        respuesta = client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 4}, headers=como_coach)
        assert respuesta.json["nivel_nuevo"] == "Avanzado"

    def test_evaluar_notifica_al_cliente_con_el_estado_anterior(self, client, daos, como_coach):
        daos["progreso"].avanzar_si_aprobo.return_value = "Avanzado"
        client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 4, "observacion": "Bien"}, headers=como_coach)
        daos["notificacion"].estado_actualizado.assert_called_once_with(3, 1, "Avanzado", "Bien")

    def test_evaluar_sin_estado(self, client, daos, como_coach):
        assert client.put("/api/coach/inscripciones/3/evaluacion", json={}, headers=como_coach).status_code == 400

    def test_estado_inexistente(self, client, daos, como_coach):
        daos["estado"].obtener_por_id.return_value = None
        assert client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 99}, headers=como_coach).status_code == 400

    def test_estado_que_no_es_de_inscripcion(self, client, daos, como_coach):
        daos["estado"].obtener_por_id.return_value = EstadoDTO(1, "Activo", "cliente,taller")
        respuesta = client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 1}, headers=como_coach)
        assert respuesta.status_code == 400
        assert respuesta.json["mensaje"] == "El estado Activo no se puede asignar a una inscripción"

    def test_inscripcion_inexistente(self, client, daos, como_coach):
        daos["inscripcion"].obtener_por_id.return_value = None
        assert client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 4}, headers=como_coach).status_code == 404

    def test_no_puede_evaluar_en_un_taller_ajeno(self, client, daos, como_coach):
        daos["taller"].tiene_personal_asignado.return_value = False
        assert client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 4}, headers=como_coach).status_code == 403

    def test_un_fallo_deshace_la_transaccion(self, client, daos, como_coach):
        daos["progreso"].avanzar_si_aprobo.side_effect = RuntimeError("fallo de base de datos")
        with pytest.raises(RuntimeError):
            client.put("/api/coach/inscripciones/3/evaluacion", json={"id_estado": 4}, headers=como_coach)
        assert daos["conexion"].rollback.called
        assert not daos["conexion"].commit.called
        daos["notificacion"].estado_actualizado.assert_not_called()
