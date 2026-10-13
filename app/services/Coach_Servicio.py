from app.models.dao.Taller_DAO import TallerDAO
from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.models.dao.Auditoria_DAO import AuditoriaDAO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Auditoria_DTO import AuditoriaDTO
from app.database.Db import Db
from app.services.Notificacion_Servicio import NotificacionServicio
from app.services.Asignacion_Taller import ROL_EN_TALLER_COACH, validar_asignacion, validar_cedula_personal
from app.services.Estado_Servicio import EstadoServicio


class CoachServicio:

    @staticmethod
    def _validar_asignacion(id_taller, cedula_personal):
        validar_asignacion(id_taller, cedula_personal, ROL_EN_TALLER_COACH)

    @staticmethod
    def listar_talleres(cedula_personal):
        validar_cedula_personal(cedula_personal)
        return TallerDAO.obtener_por_personal(cedula_personal, ROL_EN_TALLER_COACH)

    @staticmethod
    def obtener_detalle_taller(id_taller, cedula_personal):
        CoachServicio._validar_asignacion(id_taller, cedula_personal)
        return TallerDAO.obtener_detalle(id_taller)

    @staticmethod
    def registrar_actividad(id_taller, cedula_personal, id_usuario, data):
        descripcion = (data.get('descripcion') or '').strip()
        if not descripcion:
            raise ValueError("La descripción de la actividad es obligatoria")

        CoachServicio._validar_asignacion(id_taller, cedula_personal)

        actividad = AuditoriaDTO(None, id_usuario, 'taller', 'actividad', descripcion, None, id_taller)
        return AuditoriaDAO.crear(actividad)

    @staticmethod
    def evaluar_participante(id_inscripcion, cedula_personal, id_usuario, data):
        id_estado = data.get('id_estado')
        if not id_estado:
            raise ValueError("El estado de la evaluación es obligatorio")

        inscripcion = InscripcionDAO.obtener_por_id(id_inscripcion)
        if not inscripcion:
            raise LookupError("Inscripción no encontrada")

        CoachServicio._validar_asignacion(inscripcion.id_taller, cedula_personal)

        estado = EstadoServicio.validar_estado_para(id_estado, 'inscripcion')

        observacion = (data.get('observacion') or '').strip()
        descripcion = f"Evaluación del participante {inscripcion.cliente_cedula}: {estado.nombre}"
        if observacion:
            descripcion = f"{descripcion}. {observacion}"

        conexion = Db.obtener_conexion()
        try:
            InscripcionDAO.actualizar_estado(id_inscripcion, id_estado, conexion)
            AuditoriaDAO.crear(
                AuditoriaDTO(None, id_usuario, 'inscripcion', 'evaluacion', descripcion, None, inscripcion.id_taller),
                conexion
            )
            nivel_nuevo = ProgresoClienteDAO.avanzar_si_aprobo(id_inscripcion, id_usuario, conexion)
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        NotificacionServicio.estado_actualizado(id_inscripcion, inscripcion.id_estado, nivel_nuevo, observacion)
        return nivel_nuevo
