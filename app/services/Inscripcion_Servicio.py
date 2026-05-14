from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.models.dto.Inscripcion_DTO import InscripcionDTO
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
    def crear_inscripcion(data):
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
        return InscripcionDAO.crear(inscripcion)

    @staticmethod
    def actualizar_inscripcion(id_inscripcion, data):
        inscripcion = InscripcionDTO(
            id_inscripcion,
            data.get('cliente_cedula'),
            data.get('id_taller'),
            data.get('id_estado'),
            data.get('fecha_inscripcion')
        )
        return InscripcionDAO.actualizar(id_inscripcion, inscripcion)

    @staticmethod
    def eliminar_inscripcion(id_inscripcion):
        return InscripcionDAO.eliminar(id_inscripcion)
