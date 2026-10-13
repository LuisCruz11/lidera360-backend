from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.models.dto.Inscripcion_DTO import InscripcionDTO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.database.Db import Db
from app.services.Notificacion_Servicio import NotificacionServicio
from datetime import date


class InscripcionServicio:

    @staticmethod
    def listar_inscripciones():
        inscripciones = InscripcionDAO.obtener_todos()
        return [inscripcion.to_dict() for inscripcion in inscripciones]

    @staticmethod
    def obtener_inscripcion(id_inscripcion):
        inscripcion = InscripcionDAO.obtener_por_id(id_inscripcion)
        if inscripcion:
            return inscripcion.to_dict()
        return None

    @staticmethod
    def crear_inscripcion(data, id_usuario=None):
        cliente_cedula = data.get('cliente_cedula')
        id_taller = data.get('id_taller')

        if not cliente_cedula or not id_taller:
            raise ValueError("Cliente y taller son obligatorios")

        if InscripcionDAO.existe(cliente_cedula, id_taller):
            raise ValueError("El cliente ya esta inscrito en este taller")

        inscripcion = InscripcionDTO(
            None,
            cliente_cedula,
            id_taller,
            data.get('id_estado'),
            data.get('fecha_inscripcion') or date.today().isoformat()
        )

        conexion = Db.obtener_conexion()
        try:
            id_inscripcion = InscripcionDAO.crear(inscripcion, conexion)
            nivel_nuevo = ProgresoClienteDAO.avanzar_si_aprobo(id_inscripcion, id_usuario, conexion)
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        NotificacionServicio.inscripcion_creada(id_inscripcion, nivel_nuevo)
        return id_inscripcion, nivel_nuevo

    @staticmethod
    def actualizar_inscripcion(id_inscripcion, data, id_usuario=None):
        inscripcion = InscripcionDTO(
            id_inscripcion,
            data.get('cliente_cedula'),
            data.get('id_taller'),
            data.get('id_estado'),
            data.get('fecha_inscripcion')
        )

        anterior = InscripcionDAO.obtener_por_id(id_inscripcion)

        conexion = Db.obtener_conexion()
        try:
            actualizado = InscripcionDAO.actualizar(id_inscripcion, inscripcion, conexion)
            nivel_nuevo = None
            if actualizado:
                nivel_nuevo = ProgresoClienteDAO.avanzar_si_aprobo(id_inscripcion, id_usuario, conexion)
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

        if actualizado and anterior:
            NotificacionServicio.estado_actualizado(id_inscripcion, anterior.id_estado, nivel_nuevo)
        return actualizado, nivel_nuevo

    @staticmethod
    def eliminar_inscripcion(id_inscripcion):
        return InscripcionDAO.eliminar(id_inscripcion)
