from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.utils.email_service import (
    enviar_correo_cancelacion,
    enviar_correo_inscripcion,
    enviar_correo_resultado,
)

ESTADO_APROBADO = 'aprobado'
ESTADO_NO_APROBADO = 'no aprobado'


def _resultado(estado):
    """True si el estado es Aprobado, False si es No aprobado, None si no es un resultado."""
    valor = (estado or "").strip().lower()
    if valor == ESTADO_APROBADO:
        return True
    if valor == ESTADO_NO_APROBADO:
        return False
    return None


def _sin_fallar(descripcion, envio):
    # Las notificaciones se envían después de guardar: si el correo falla, la acción
    # del usuario ya quedó registrada y solo se deja constancia en el log.
    try:
        envio()
    except Exception as error:
        print(f"No se pudo enviar la notificación de {descripcion}: {error}", flush=True)


class NotificacionServicio:

    @staticmethod
    def inscripcion_creada(id_inscripcion, nivel_nuevo=None):
        """Avisa al cliente de una inscripción nueva. Si se creó ya evaluada, envía el resultado."""
        def envio():
            datos = InscripcionDAO.obtener_datos_notificacion(id_inscripcion)
            if not datos or not datos.get("correo"):
                return
            resultado = _resultado(datos.get("estado"))
            if resultado is None:
                enviar_correo_inscripcion(datos)
            else:
                enviar_correo_resultado(datos, resultado, nivel_nuevo)

        _sin_fallar("inscripción", envio)

    @staticmethod
    def estado_actualizado(id_inscripcion, id_estado_anterior, nivel_nuevo=None, observacion=""):
        """Avisa el resultado (Aprobado / No aprobado) solo si el estado realmente cambió."""
        def envio():
            inscripcion = InscripcionDAO.obtener_por_id(id_inscripcion)
            if not inscripcion or str(inscripcion.id_estado) == str(id_estado_anterior):
                return
            datos = InscripcionDAO.obtener_datos_notificacion(id_inscripcion)
            if not datos or not datos.get("correo"):
                return
            resultado = _resultado(datos.get("estado"))
            if resultado is None:
                return
            enviar_correo_resultado(datos, resultado, nivel_nuevo, observacion)

        _sin_fallar("resultado", envio)

    @staticmethod
    def datos_para_cancelacion(id_inscripcion):
        """Se consulta antes de borrar la inscripción, porque después ya no existen los datos."""
        try:
            return InscripcionDAO.obtener_datos_notificacion(id_inscripcion)
        except Exception as error:
            print(f"No se pudieron obtener los datos para notificar la cancelación: {error}", flush=True)
            return None

    @staticmethod
    def inscripcion_cancelada(datos):
        if not datos or not datos.get("correo"):
            return
        _sin_fallar("cancelación", lambda: enviar_correo_cancelacion(datos))
