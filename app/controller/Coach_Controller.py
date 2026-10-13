from app.services.Coach_Servicio import CoachServicio


class CoachController:

    @staticmethod
    def obtener_talleres(cedula_personal):
        return CoachServicio.listar_talleres(cedula_personal)

    @staticmethod
    def obtener_detalle_taller(id_taller, cedula_personal):
        return CoachServicio.obtener_detalle_taller(id_taller, cedula_personal)

    @staticmethod
    def registrar_actividad(id_taller, cedula_personal, id_usuario, data):
        return CoachServicio.registrar_actividad(id_taller, cedula_personal, id_usuario, data)

    @staticmethod
    def evaluar_participante(id_inscripcion, cedula_personal, id_usuario, data):
        return CoachServicio.evaluar_participante(id_inscripcion, cedula_personal, id_usuario, data)
