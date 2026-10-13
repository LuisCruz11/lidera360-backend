"""Personal capacitado: solo sus talleres y participantes, notas y registro de asistencia."""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.models.dao.Asistencia_DAO import AsistenciaDAO
from app.models.dto.Taller_DTO import TallerDTO

HOY = date.today()
TALLER_EN_CURSO = TallerDTO(5, "Taller", 1, HOY - timedelta(days=3), HOY + timedelta(days=3), 1)
SERVICIO = "app.services.Personal_Capacitado_Servicio."
URL = "/api/personal-capacitado"


@pytest.fixture
def daos():
    taller_dao = MagicMock()
    taller_dao.obtener_por_id.return_value = TALLER_EN_CURSO
    taller_dao.tiene_personal_asignado.return_value = True
    taller_dao.obtener_por_personal.return_value = [{"id_taller": 5}]
    taller_dao.obtener_detalle.return_value = {"taller": {}, "clientes_inscritos": [], "notas": []}

    with patch("app.services.Asignacion_Taller.TallerDAO", taller_dao), \
            patch(SERVICIO + "TallerDAO", taller_dao), \
            patch(SERVICIO + "ClienteDAO") as cliente_dao, \
            patch(SERVICIO + "AsistenciaDAO") as asistencia_dao, \
            patch(SERVICIO + "TallerServicio") as taller_servicio:
        cliente_dao.obtener_por_personal_asignado.return_value = []
        asistencia_dao.obtener_por_taller_y_fecha.return_value = [{"id_inscripcion": 1}]
        asistencia_dao.guardar.return_value = (2, 3)
        taller_servicio.agregar_nota.return_value = 44
        yield {"taller": taller_dao, "cliente": cliente_dao, "asistencia": asistencia_dao}


def _asistencia(fecha, registros=None):
    return {
        "fecha": fecha.isoformat() if isinstance(fecha, date) else fecha,
        "registros": registros if registros is not None else [
            {"id_inscripcion": 1, "asistio": True},
            {"id_inscripcion": 2, "asistio": False},
        ],
    }


class TestAcceso:

    def test_ve_solo_sus_talleres(self, client, daos, como_personal_capacitado):
        assert client.get(f"{URL}/talleres", headers=como_personal_capacitado).status_code == 200
        daos["taller"].obtener_por_personal.assert_called_once_with("1107974839", "personal capacitado")

    def test_ve_solo_los_participantes_de_sus_talleres(self, client, daos, como_personal_capacitado):
        assert client.get(f"{URL}/clientes", headers=como_personal_capacitado).status_code == 200
        daos["cliente"].obtener_por_personal_asignado.assert_called_once_with("1107974839", "personal capacitado")

    def test_un_coach_no_puede_entrar(self, client, daos, como_coach):
        assert client.get(f"{URL}/talleres", headers=como_coach).status_code == 403

    def test_ya_no_ve_todos_los_talleres_ni_clientes(self, client, como_personal_capacitado):
        assert client.get("/api/talleres/", headers=como_personal_capacitado).status_code == 403
        assert client.get("/api/clientes/", headers=como_personal_capacitado).status_code == 403

    def test_el_coordinador_sigue_viendo_todos_los_talleres(self, client, como_coordinador):
        with patch("app.routes.Taller_rutas.TallerController") as controlador:
            controlador.obtener_talleres.return_value = []
            assert client.get("/api/talleres/", headers=como_coordinador).status_code == 200

    def test_taller_ajeno(self, client, daos, como_personal_capacitado):
        daos["taller"].tiene_personal_asignado.return_value = False
        assert client.get(f"{URL}/talleres/5", headers=como_personal_capacitado).status_code == 403
        assert client.put(f"{URL}/talleres/5/asistencia", json=_asistencia(HOY),
                          headers=como_personal_capacitado).status_code == 403

    def test_taller_inexistente(self, client, daos, como_personal_capacitado):
        daos["taller"].obtener_por_id.return_value = None
        assert client.get(f"{URL}/talleres/99", headers=como_personal_capacitado).status_code == 404


class TestNotasYDetalle:

    def test_detalle(self, client, daos, como_personal_capacitado):
        assert client.get(f"{URL}/talleres/5", headers=como_personal_capacitado).status_code == 200

    def test_agregar_nota(self, client, daos, como_personal_capacitado):
        respuesta = client.post(f"{URL}/talleres/5/notas", json={"descripcion": "Apoyo logístico"},
                                headers=como_personal_capacitado)
        assert respuesta.status_code == 201


class TestAsistencia:

    def test_consultar_asistencia_de_una_fecha(self, client, daos, como_personal_capacitado):
        respuesta = client.get(f"{URL}/talleres/5/asistencia?fecha={HOY.isoformat()}", headers=como_personal_capacitado)
        assert respuesta.status_code == 200
        assert respuesta.json["fecha"] == HOY.isoformat()

    def test_fecha_con_formato_invalido(self, client, daos, como_personal_capacitado):
        assert client.get(f"{URL}/talleres/5/asistencia?fecha=ayer", headers=como_personal_capacitado).status_code == 400

    def test_guardar_asistencia(self, client, daos, como_personal_capacitado):
        respuesta = client.put(f"{URL}/talleres/5/asistencia", json=_asistencia(HOY), headers=como_personal_capacitado)
        assert respuesta.status_code == 200
        assert respuesta.json == {"mensaje": "Asistencia registrada", "presentes": 2, "total": 3}
        id_taller, fecha, registros, id_usuario = daos["asistencia"].guardar.call_args[0]
        assert (id_taller, fecha, registros, id_usuario) == (5, HOY, [(1, True), (2, False)], "6")

    @pytest.mark.parametrize("fecha, mensaje", [
        (HOY + timedelta(days=1), "No puedes registrar asistencia de una fecha futura"),
        (HOY - timedelta(days=10), "La fecha es anterior al inicio del taller"),
    ], ids=["fecha-futura", "antes-del-taller"])
    def test_valida_la_fecha_de_la_sesion(self, client, daos, como_personal_capacitado, fecha, mensaje):
        respuesta = client.put(f"{URL}/talleres/5/asistencia", json=_asistencia(fecha), headers=como_personal_capacitado)
        assert respuesta.status_code == 400
        assert respuesta.json["mensaje"] == mensaje

    def test_fecha_posterior_al_fin_del_taller(self, client, daos, como_personal_capacitado):
        daos["taller"].obtener_por_id.return_value = TallerDTO(5, "T", 1, HOY - timedelta(days=10), HOY - timedelta(days=5), 1)
        respuesta = client.put(f"{URL}/talleres/5/asistencia", json=_asistencia(HOY - timedelta(days=2)),
                               headers=como_personal_capacitado)
        assert respuesta.json["mensaje"] == "La fecha es posterior al fin del taller"

    @pytest.mark.parametrize("registros", [[], [{"x": 1}], "no-es-lista"], ids=["vacio", "mal-formado", "no-lista"])
    def test_valida_los_registros(self, client, daos, como_personal_capacitado, registros):
        respuesta = client.put(f"{URL}/talleres/5/asistencia", json=_asistencia(HOY, registros),
                               headers=como_personal_capacitado)
        assert respuesta.status_code == 400


@pytest.fixture
def conexion_asistencia():
    with patch("app.models.dao.Asistencia_DAO.Db") as db:
        conexion = MagicMock()
        conexion.cursor.return_value.fetchall.return_value = [(1,), (2,)]
        db.obtener_conexion.return_value = conexion
        yield conexion


class TestAsistenciaDAO:

    def test_guarda_y_registra_en_bitacora(self, conexion_asistencia):
        assert AsistenciaDAO.guardar(5, HOY, [(1, True), (2, False)], "6") == (1, 2)
        filas = conexion_asistencia.cursor.return_value.executemany.call_args[0][1]
        assert filas == [(1, HOY, 1, "6"), (2, HOY, 0, "6")]
        assert conexion_asistencia.commit.called

    def test_rechaza_inscripciones_de_otro_taller(self, conexion_asistencia):
        with pytest.raises(ValueError, match="no pertenecen a este taller"):
            AsistenciaDAO.guardar(5, HOY, [(1, True), (9, False)], "6")
        assert conexion_asistencia.rollback.called
        assert not conexion_asistencia.commit.called
