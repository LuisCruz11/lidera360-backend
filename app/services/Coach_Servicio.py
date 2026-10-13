from app.models.dao.Taller_DAO import TallerDAO
from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.models.dao.Estado_DAO import EstadoDAO
from app.models.dao.Auditoria_DAO import AuditoriaDAO
from app.models.dto.Auditoria_DTO import AuditoriaDTO
from app.database.Db import Db

ROL_EN_TALLER_COACH = 'coach'


class CoachServicio:

    @staticmethod
    def _validar_cedula_personal(cedula_personal):
        if not cedula_personal:
            raise PermissionError("Tu usuario no está vinculado a un registro de personal")

    @staticmethod
    def _validar_asignacion(id_taller, cedula_personal):
        CoachServicio._validar_cedula_personal(cedula_personal)
        if not TallerDAO.obtener_por_id(id_taller):
            raise LookupError("Taller no encontrado")
        if not TallerDAO.tiene_personal_asignado(id_taller, cedula_personal, ROL_EN_TALLER_COACH):
            raise PermissionError("No estás asignado como coach de este taller")

    @staticmethod
    def listar_talleres(cedula_personal):
        CoachServicio._validar_cedula_personal(cedula_personal)
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

        estado = EstadoDAO.obtener_por_id(id_estado)
        if not estado:
            raise ValueError("El estado seleccionado no existe")

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
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()
