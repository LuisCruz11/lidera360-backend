"""Auditoría de las acciones del coordinador, integridad de la tabla y reporte de auditoría."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from openpyxl import load_workbook

from app.models.dao.Taller_DAO import TallerDAO
from app.models.dto.Cliente_DTO import ClienteDTO
from app.models.dto.Estado_DTO import EstadoDTO
from app.models.dto.Inscripcion_DTO import InscripcionDTO
from app.models.dto.Taller_DTO import TallerDTO
from app.utils import fechas

DESCRIPCIONES = "app.utils.descripciones_auditoria."


def _registro(auditoria_dao, indice=-1):
    return auditoria_dao.crear.call_args_list[indice][0][0]


@pytest.fixture
def daos_descripcion():
    with patch(DESCRIPCIONES + "ClienteDAO") as cliente, patch(DESCRIPCIONES + "TallerDAO") as taller, \
            patch(DESCRIPCIONES + "EstadoDAO") as estado, patch(DESCRIPCIONES + "InscripcionDAO") as inscripcion, \
            patch(DESCRIPCIONES + "TipoTallerDAO") as nivel, patch(DESCRIPCIONES + "PersonalDAO") as personal, \
            patch(DESCRIPCIONES + "RolDAO") as rol:
        cliente.obtener_por_cedula.return_value = ClienteDTO("222", "Ana", "Pérez", "a@b.co", "300", "F", 20, 1)
        taller.obtener_por_id.return_value = TallerDTO(5, "Liderazgo 1", 1, None, None, 1)
        estado.obtener_por_id.side_effect = lambda id_estado: EstadoDTO(id_estado, {3: "Iniciado", 4: "Aprobado"}.get(int(id_estado), "Activo"))
        inscripcion.obtener_por_id.return_value = InscripcionDTO(3, "222", 5, 3, None)
        nivel.obtener_por_id.return_value = MagicMock(nombre="Basico")
        personal.obtener_por_cedula.return_value = MagicMock(nombres="Carlos", apellidos="Ruiz")
        rol.obtener_por_id.return_value = MagicMock(nombre="Coach")
        yield {"cliente": cliente, "taller": taller}


class TestRegistroDeAcciones:

    def test_crear_cliente(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        with patch("app.routes.Cliente_rutas.ClienteController"):
            client.post("/api/clientes/", headers=como_coordinador, json={
                "cedula": "222", "nombres": "Ana", "apellidos": "Pérez", "sexo": "F", "edad": 20,
                "id_estado": 1, "username": "ana", "password": "Clave123!",
            })
        registro = _registro(auditoria_dao)
        assert (registro.tabla, registro.accion, registro.id_usuario) == ("clientes", "crear", "3")
        assert registro.descripcion == "Creó el cliente 222 - Ana Pérez"

    def test_si_la_accion_falla_no_se_registra(self, client, auditoria_dao, como_coordinador):
        with patch("app.routes.Cliente_rutas.ClienteController") as controlador:
            controlador.crear_cliente.side_effect = ValueError("La cedula ya esta registrada")
            client.post("/api/clientes/", headers=como_coordinador, json={
                "cedula": "222", "nombres": "Ana", "apellidos": "Pérez", "sexo": "F", "edad": 20,
                "id_estado": 1, "username": "ana", "password": "Clave123!",
            })
        auditoria_dao.crear.assert_not_called()

    def test_eliminar_guarda_el_nombre_antes_de_borrar(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        orden = []
        daos_descripcion["cliente"].obtener_por_cedula.side_effect = lambda cedula: (
            orden.append("leer nombre") or ClienteDTO(cedula, "Ana", "Pérez", None, None, None, None, 1)
        )
        with patch("app.routes.Cliente_rutas.ClienteController") as controlador:
            controlador.eliminar_cliente.side_effect = lambda cedula: orden.append("eliminar") or True
            client.delete("/api/clientes/222", headers=como_coordinador)
        assert orden == ["leer nombre", "eliminar"]
        assert _registro(auditoria_dao).descripcion == "Eliminó el cliente 222 - Ana Pérez"

    def test_crear_taller_queda_vinculado_al_taller(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        with patch("app.routes.Taller_rutas.TallerController") as controlador:
            controlador.crear_taller.return_value = 42
            client.post("/api/talleres/", headers=como_coordinador, json={
                "nombre": "Liderazgo 1", "id_tipo_taller": 1, "fecha_inicio": "2026-10-16", "fecha_fin": "2026-10-18",
                "id_estado": 1, "personal_asignado": [{"cedula_personal": "111", "rol_en_taller": "Coach"}],
            })
        registro = _registro(auditoria_dao)
        assert registro.id_taller == 42
        assert "Creó el taller Liderazgo 1" in registro.descripcion
        assert "Coach: Carlos Ruiz" in registro.descripcion

    def test_eliminar_taller_no_lo_vincula(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        with patch("app.routes.Taller_rutas.TallerController") as controlador:
            controlador.eliminar_taller.return_value = True
            client.delete("/api/talleres/5", headers=como_coordinador)
        registro = _registro(auditoria_dao)
        assert registro.id_taller is None
        assert registro.descripcion.startswith("Eliminó el taller Liderazgo 1 (id 5)")

    def test_actualizar_inscripcion_muestra_el_cambio_de_estado(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        with patch("app.routes.Inscripcion_rutas.InscripcionController") as controlador:
            controlador.actualizar_inscripcion.return_value = (True, "Avanzado")
            client.put("/api/inscripciones/3", headers=como_coordinador,
                       json={"cliente_cedula": "222", "id_taller": 5, "id_estado": 4})
        descripcion = _registro(auditoria_dao).descripcion
        assert "estado: Iniciado → Aprobado" in descripcion
        assert "El cliente subió al nivel Avanzado" in descripcion

    def test_generar_reporte(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        with patch("app.routes.Reporte_rutas.ReporteController") as controlador:
            controlador.generar.return_value = (b"xlsx", "reporte.xlsx")
            client.get("/api/reportes/inscripciones?fecha_desde=2026-10-01&id_taller=5", headers=como_coordinador)
        registro = _registro(auditoria_dao)
        assert (registro.tabla, registro.accion) == ("reportes", "generar")
        assert registro.descripcion == "Generó el reporte Inscripciones (filtros: desde 2026-10-01, taller: Liderazgo 1)"

    def test_un_fallo_al_auditar_no_afecta_la_accion(self, client, auditoria_dao, daos_descripcion, como_coordinador):
        auditoria_dao.crear.side_effect = RuntimeError("MySQL caído")
        with patch("app.routes.Taller_rutas.TallerController") as controlador:
            controlador.eliminar_taller.return_value = True
            respuesta = client.delete("/api/talleres/5", headers=como_coordinador)
        assert respuesta.status_code == 200

    @pytest.mark.parametrize("metodo, ruta, controlador, metodo_controlador, valor", [
        ("put", "/api/clientes/222", "app.routes.Cliente_rutas.ClienteController", "actualizar_cliente", True),
        ("put", "/api/talleres/5", "app.routes.Taller_rutas.TallerController", "actualizar_taller", True),
        ("delete", "/api/personal/111", "app.routes.Personal_rutas.PersonalController", "eliminar_persona", True),
        ("delete", "/api/inscripciones/3", "app.routes.Inscripcion_rutas.InscripcionController", "eliminar_inscripcion", True),
        ("delete", "/api/usuarios/9", "app.routes.Usuario_rutas.UsuarioController", "eliminar_usuario", True),
    ], ids=["editar-cliente", "editar-taller", "eliminar-personal", "eliminar-inscripcion", "eliminar-usuario"])
    def test_otras_acciones_del_coordinador_quedan_registradas(
            self, client, auditoria_dao, daos_descripcion, como_coordinador, metodo, ruta, controlador, metodo_controlador, valor):
        cuerpo = {"nombres": "Ana", "apellidos": "Pérez", "sexo": "F", "edad": 20, "id_estado": 1,
                  "nombre": "Liderazgo 1", "id_tipo_taller": 1, "fecha_inicio": "2026-10-16", "fecha_fin": "2026-10-18"}
        with patch(controlador) as falso, patch(DESCRIPCIONES + "UsuarioDAO"):
            getattr(falso, metodo_controlador).return_value = valor
            getattr(client, metodo)(ruta, headers=como_coordinador, json=cuerpo)
        auditoria_dao.crear.assert_called_once()


class TestIntegridad:

    @pytest.mark.parametrize("metodo", ["post", "put", "delete"])
    def test_la_auditoria_no_se_puede_modificar_por_la_api(self, client, como_coordinador, metodo):
        ruta = "/api/auditorias/" if metodo == "post" else "/api/auditorias/1"
        assert getattr(client, metodo)(ruta, headers=como_coordinador, json={}).status_code == 405

    def test_eliminar_un_taller_conserva_su_auditoria(self):
        with patch("app.models.dao.Taller_DAO.Db") as db:
            conexion = MagicMock()
            conexion.cursor.return_value.rowcount = 1
            db.obtener_conexion.return_value = conexion
            TallerDAO.eliminar(5)
        consultas = " ".join(llamada[0][0] for llamada in conexion.cursor.return_value.execute.call_args_list)
        assert "UPDATE auditoria SET id_taller = NULL" in consultas
        assert "DELETE FROM auditoria" not in consultas


class TestHoraDeColombia:

    def test_hoy_usa_utc_menos_5(self):
        utc_noche = datetime(2026, 10, 14, 2, 0, tzinfo=timezone.utc)
        with patch("app.utils.fechas.datetime") as reloj:
            reloj.now.side_effect = lambda zona: utc_noche.astimezone(zona)
            assert fechas.hoy().isoformat() == "2026-10-13"

    def test_la_conexion_mysql_usa_hora_de_colombia(self):
        from app.database.Db import Db
        with patch("pymysql.connect", MagicMock()) as conectar:
            Db.obtener_conexion()
        assert conectar.call_args.kwargs["init_command"] == "SET time_zone = '-05:00'"


class TestReporteAuditoria:

    def test_excel_con_fecha_y_hora(self, client, como_coordinador):
        fila = {"fecha": datetime(2026, 10, 13, 21, 30), "usuario": None, "rol": None, "tabla": "clientes",
                "accion": "crear", "descripcion": "Creó el cliente 222 - Ana Pérez", "taller": None}
        with patch("app.services.Reporte_Servicio.ReporteDAO") as dao, \
                patch(DESCRIPCIONES + "TallerDAO"):
            dao.auditoria.return_value = [fila]
            respuesta = client.get("/api/reportes/auditoria?fecha_desde=2026-10-01", headers=como_coordinador)
        hoja = load_workbook(BytesIO(respuesta.data)).active
        encabezados = [celda.value for celda in hoja[5]]
        datos = dict(zip(encabezados, [celda.value for celda in hoja[6]]))
        assert hoja["A1"].value == "Auditoría"
        assert datos["Fecha y hora"] == datetime(2026, 10, 13, 21, 30)
        assert hoja["A6"].number_format == "DD/MM/YYYY HH:MM"
        assert datos["Usuario"] == "(usuario eliminado)"
        assert datos["Módulo"] == "Clientes"
        dao.auditoria.assert_called_once()
        assert dao.auditoria.call_args[0][0].isoformat() == "2026-10-01"

    def test_filtro_hasta_incluye_todo_el_dia(self):
        from app.models.dao.Reporte_DAO import ReporteDAO
        with patch("app.models.dao.Reporte_DAO._consultar") as consultar:
            ReporteDAO.auditoria(None, "2026-10-13")
        sql, parametros = consultar.call_args[0]
        assert "a.fecha < DATE_ADD(%s, INTERVAL 1 DAY)" in sql
        assert parametros == ("2026-10-13",)
