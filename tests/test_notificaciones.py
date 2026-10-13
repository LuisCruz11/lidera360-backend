"""Notificaciones por correo al cliente: inscripción, resultado y cancelación."""
import json
from datetime import date
from unittest.mock import patch

import pytest

from app.models.dto.Inscripcion_DTO import InscripcionDTO
from app.services.Notificacion_Servicio import NotificacionServicio
from app.utils import email_service

MODULO = "app.services.Notificacion_Servicio."
DATOS = {
    "nombres": "Ana", "correo": "ana@correo.co", "taller": "Liderazgo 1", "nivel": "Basico",
    "fecha_inicio": date(2026, 10, 16), "fecha_fin": date(2026, 10, 18), "coach": "Carlos Ruiz",
    "estado": "Iniciado", "es_ultimo_nivel": 0,
}


@pytest.fixture
def notificacion():
    with patch(MODULO + "InscripcionDAO") as dao, \
            patch(MODULO + "enviar_correo_inscripcion") as inscripcion, \
            patch(MODULO + "enviar_correo_resultado") as resultado, \
            patch(MODULO + "enviar_correo_cancelacion") as cancelacion:
        dao.obtener_datos_notificacion.return_value = dict(DATOS)
        dao.obtener_por_id.return_value = InscripcionDTO(3, "222", 5, 4, None)
        yield {"dao": dao, "inscripcion": inscripcion, "resultado": resultado, "cancelacion": cancelacion}


def _con_estado(notificacion, estado):
    notificacion["dao"].obtener_datos_notificacion.return_value = {**DATOS, "estado": estado}


class TestInscripcionCreada:

    def test_confirma_la_inscripcion(self, notificacion):
        NotificacionServicio.inscripcion_creada(3)
        notificacion["inscripcion"].assert_called_once()
        notificacion["resultado"].assert_not_called()

    def test_si_se_crea_ya_aprobada_envia_el_resultado(self, notificacion):
        _con_estado(notificacion, "Aprobado")
        NotificacionServicio.inscripcion_creada(3, "Avanzado")
        notificacion["resultado"].assert_called_once_with({**DATOS, "estado": "Aprobado"}, True, "Avanzado")
        notificacion["inscripcion"].assert_not_called()

    def test_cliente_sin_correo(self, notificacion):
        notificacion["dao"].obtener_datos_notificacion.return_value = {**DATOS, "correo": None}
        NotificacionServicio.inscripcion_creada(3)
        notificacion["inscripcion"].assert_not_called()


class TestEstadoActualizado:

    @pytest.mark.parametrize("estado, aprobado", [("Aprobado", True), ("No aprobado", False)])
    def test_avisa_el_resultado(self, notificacion, estado, aprobado):
        _con_estado(notificacion, estado)
        NotificacionServicio.estado_actualizado(3, id_estado_anterior=3, nivel_nuevo=None, observacion="Bien")
        notificacion["resultado"].assert_called_once_with({**DATOS, "estado": estado}, aprobado, None, "Bien")

    def test_no_avisa_si_el_estado_no_cambio(self, notificacion):
        _con_estado(notificacion, "Aprobado")
        NotificacionServicio.estado_actualizado(3, id_estado_anterior=4)
        notificacion["resultado"].assert_not_called()

    def test_no_avisa_estados_que_no_son_resultado(self, notificacion):
        _con_estado(notificacion, "Iniciado")
        NotificacionServicio.estado_actualizado(3, id_estado_anterior=1)
        notificacion["resultado"].assert_not_called()


class TestFallosNoAfectanAlUsuario:

    def test_un_error_del_correo_no_se_propaga(self, notificacion):
        notificacion["inscripcion"].side_effect = RuntimeError("Brevo caído")
        NotificacionServicio.inscripcion_creada(3)

    def test_un_error_de_base_de_datos_no_se_propaga(self, notificacion):
        notificacion["dao"].obtener_por_id.side_effect = RuntimeError("MySQL caído")
        NotificacionServicio.estado_actualizado(3, id_estado_anterior=3)
        assert NotificacionServicio.datos_para_cancelacion(3) is not None
        notificacion["dao"].obtener_datos_notificacion.side_effect = RuntimeError("MySQL caído")
        assert NotificacionServicio.datos_para_cancelacion(3) is None


class TestCancelacion:

    def test_avisa_la_cancelacion(self, notificacion):
        NotificacionServicio.inscripcion_cancelada(dict(DATOS))
        notificacion["cancelacion"].assert_called_once()

    def test_sin_datos_no_envia(self, notificacion):
        NotificacionServicio.inscripcion_cancelada(None)
        notificacion["cancelacion"].assert_not_called()


@pytest.fixture
def correo_enviado(app):
    """Ejecuta una plantilla y devuelve (asunto, texto, html) del correo que se habría enviado."""
    def _enviar(funcion, *args):
        with app.app_context(), patch("urllib.request.urlopen") as abrir:
            abrir.return_value.__enter__.return_value.read.return_value = b"{}"
            funcion(*args)
            cuerpo = json.loads(abrir.call_args[0][0].data)
        return cuerpo["subject"], cuerpo["textContent"], cuerpo["htmlContent"]
    return _enviar


class TestPlantillas:

    def test_inscripcion_incluye_el_detalle_del_taller(self, correo_enviado):
        asunto, texto, _ = correo_enviado(email_service.enviar_correo_inscripcion, DATOS)
        assert asunto == "Inscripción confirmada: Liderazgo 1"
        assert "del 16 de octubre de 2026 al 18 de octubre de 2026" in texto
        assert "Coach: Carlos Ruiz" in texto
        assert "https://frontend.pruebas" in texto

    def test_aprobado_con_avance_de_nivel(self, correo_enviado):
        asunto, texto, _ = correo_enviado(email_service.enviar_correo_resultado, DATOS, True, "Avanzado", "Excelente")
        assert asunto == "¡Aprobaste el taller Liderazgo 1!"
        assert "Subiste al nivel Avanzado" in texto
        assert "Comentario de tu coach: Excelente" in texto

    def test_aprobado_en_el_ultimo_nivel(self, correo_enviado):
        _, texto, _ = correo_enviado(email_service.enviar_correo_resultado, {**DATOS, "es_ultimo_nivel": 1}, True)
        assert "completaste todos los niveles" in texto

    def test_no_aprobado(self, correo_enviado):
        asunto, texto, _ = correo_enviado(email_service.enviar_correo_resultado, DATOS, False)
        assert asunto == "Resultado del taller Liderazgo 1"
        assert "No aprobado" in texto
        assert "Subiste" not in texto

    def test_cancelacion(self, correo_enviado):
        asunto, _, _ = correo_enviado(email_service.enviar_correo_cancelacion, DATOS)
        assert asunto == "Inscripción cancelada: Liderazgo 1"

    def test_escapa_html_en_los_datos(self, correo_enviado):
        _, _, html = correo_enviado(email_service.enviar_correo_inscripcion, {**DATOS, "taller": "<b>Taller</b>"})
        assert "<b>Taller</b>" not in html
        assert "&lt;b&gt;Taller&lt;/b&gt;" in html


class TestEventosDisparanNotificacion:

    def test_inscripcion_del_cliente(self, client, como_cliente):
        with patch("app.services.Cliente_Servicio.ClienteDAO") as dao, \
                patch("app.services.Cliente_Servicio.NotificacionServicio") as notificar:
            dao.inscribir_en_taller.return_value = 15
            respuesta = client.post("/api/clientes/222/inscripciones", json={"id_taller": 5}, headers=como_cliente)
        assert respuesta.status_code == 201
        notificar.inscripcion_creada.assert_called_once_with(15)

    def test_cancelacion_del_cliente(self, client, como_cliente):
        with patch("app.services.Cliente_Servicio.ClienteDAO") as dao, \
                patch("app.services.Cliente_Servicio.NotificacionServicio") as notificar:
            notificar.datos_para_cancelacion.return_value = DATOS
            client.delete("/api/clientes/222/inscripciones/3", headers=como_cliente)
        dao.cancelar_inscripcion.assert_called_once()
        notificar.inscripcion_cancelada.assert_called_once_with(DATOS)

    def test_si_la_cancelacion_falla_no_se_notifica(self, client, como_cliente):
        with patch("app.services.Cliente_Servicio.ClienteDAO") as dao, \
                patch("app.services.Cliente_Servicio.NotificacionServicio") as notificar:
            dao.cancelar_inscripcion.side_effect = ValueError("Solo puedes cancelar inscripciones en estado Iniciado")
            respuesta = client.delete("/api/clientes/222/inscripciones/3", headers=como_cliente)
        assert respuesta.status_code == 400
        notificar.inscripcion_cancelada.assert_not_called()
