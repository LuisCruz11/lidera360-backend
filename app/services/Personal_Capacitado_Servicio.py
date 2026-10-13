from datetime import date

from app.models.dao.Asistencia_DAO import AsistenciaDAO
from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dao.Taller_DAO import TallerDAO
from app.services.Asignacion_Taller import (
    ROL_EN_TALLER_PERSONAL_CAPACITADO,
    validar_asignacion,
    validar_cedula_personal,
)
from app.services.Taller_Servicio import TallerServicio
from app.utils.fechas import hoy


def _validar(id_taller, cedula_personal):
    validar_asignacion(id_taller, cedula_personal, ROL_EN_TALLER_PERSONAL_CAPACITADO)


def _convertir_fecha(valor):
    try:
        return date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD")


def _validar_fecha_sesion(id_taller, fecha):
    taller = TallerDAO.obtener_por_id(id_taller)
    if taller.fecha_inicio and fecha < taller.fecha_inicio:
        raise ValueError("La fecha es anterior al inicio del taller")
    if taller.fecha_fin and fecha > taller.fecha_fin:
        raise ValueError("La fecha es posterior al fin del taller")
    if fecha > hoy():
        raise ValueError("No puedes registrar asistencia de una fecha futura")


class PersonalCapacitadoServicio:

    @staticmethod
    def listar_talleres(cedula_personal):
        validar_cedula_personal(cedula_personal)
        return TallerDAO.obtener_por_personal(cedula_personal, ROL_EN_TALLER_PERSONAL_CAPACITADO)

    @staticmethod
    def listar_clientes(cedula_personal):
        validar_cedula_personal(cedula_personal)
        return ClienteDAO.obtener_por_personal_asignado(cedula_personal, ROL_EN_TALLER_PERSONAL_CAPACITADO)

    @staticmethod
    def obtener_detalle_taller(id_taller, cedula_personal):
        _validar(id_taller, cedula_personal)
        return TallerDAO.obtener_detalle(id_taller)

    @staticmethod
    def agregar_nota(id_taller, cedula_personal, id_usuario, data):
        _validar(id_taller, cedula_personal)
        return TallerServicio.agregar_nota(id_taller, id_usuario, data)

    @staticmethod
    def obtener_asistencia(id_taller, cedula_personal, fecha):
        _validar(id_taller, cedula_personal)
        fecha_sesion = _convertir_fecha(fecha)
        return {
            "fecha": fecha_sesion.isoformat(),
            "participantes": AsistenciaDAO.obtener_por_taller_y_fecha(id_taller, fecha_sesion),
        }

    @staticmethod
    def registrar_asistencia(id_taller, cedula_personal, id_usuario, data):
        _validar(id_taller, cedula_personal)
        fecha_sesion = _convertir_fecha(data.get('fecha'))
        _validar_fecha_sesion(id_taller, fecha_sesion)

        registros = data.get('registros')
        if not isinstance(registros, list) or not registros:
            raise ValueError("Debes enviar la asistencia de al menos un participante")

        try:
            pares = [(int(registro['id_inscripcion']), bool(registro['asistio'])) for registro in registros]
        except (KeyError, TypeError, ValueError):
            raise ValueError("Cada registro debe tener id_inscripcion y asistio")

        return AsistenciaDAO.guardar(id_taller, fecha_sesion, pares, id_usuario)
