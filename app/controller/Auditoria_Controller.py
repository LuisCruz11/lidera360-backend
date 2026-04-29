from app.services.Auditoria_Servicio import AuditoriaServicio


class AuditoriaController:

    @staticmethod
    def obtener_auditorias():
        return AuditoriaServicio.listar_auditorias()

    @staticmethod
    def obtener_auditoria(id_auditoria):
        return AuditoriaServicio.obtener_auditoria(id_auditoria)

    @staticmethod
    def crear_auditoria(data):
        return AuditoriaServicio.crear_auditoria(data)

    @staticmethod
    def actualizar_auditoria(id_auditoria, data):
        return AuditoriaServicio.actualizar_auditoria(id_auditoria, data)

    @staticmethod
    def eliminar_auditoria(id_auditoria):
        return AuditoriaServicio.eliminar_auditoria(id_auditoria)
