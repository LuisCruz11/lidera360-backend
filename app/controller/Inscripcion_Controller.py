from app.services.Inscripcion_Servicio import InscripcionServicio


class InscripcionController:

    @staticmethod
    def obtener_inscripciones():
        return InscripcionServicio.listar_inscripciones()

    @staticmethod
    def obtener_inscripcion(id_inscripcion):
        return InscripcionServicio.obtener_inscripcion(id_inscripcion)

    @staticmethod
    def crear_inscripcion(data):
        return InscripcionServicio.crear_inscripcion(data)

    @staticmethod
    def actualizar_inscripcion(id_inscripcion, data):
        return InscripcionServicio.actualizar_inscripcion(id_inscripcion, data)

    @staticmethod
    def eliminar_inscripcion(id_inscripcion):
        return InscripcionServicio.eliminar_inscripcion(id_inscripcion)
