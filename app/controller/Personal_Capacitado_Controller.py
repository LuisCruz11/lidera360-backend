from app.services.Personal_Capacitado_Servicio import PersonalCapacitadoServicio


class PersonalCapacitadoController:

    @staticmethod
    def obtener_talleres(cedula_personal):
        return PersonalCapacitadoServicio.listar_talleres(cedula_personal)

    @staticmethod
    def obtener_clientes(cedula_personal):
        return PersonalCapacitadoServicio.listar_clientes(cedula_personal)

    @staticmethod
    def obtener_detalle_taller(id_taller, cedula_personal):
        return PersonalCapacitadoServicio.obtener_detalle_taller(id_taller, cedula_personal)

    @staticmethod
    def agregar_nota(id_taller, cedula_personal, id_usuario, data):
        return PersonalCapacitadoServicio.agregar_nota(id_taller, cedula_personal, id_usuario, data)

    @staticmethod
    def obtener_asistencia(id_taller, cedula_personal, fecha):
        return PersonalCapacitadoServicio.obtener_asistencia(id_taller, cedula_personal, fecha)

    @staticmethod
    def registrar_asistencia(id_taller, cedula_personal, id_usuario, data):
        return PersonalCapacitadoServicio.registrar_asistencia(id_taller, cedula_personal, id_usuario, data)
