from app.services.Auditoria_Servicio import AuditoriaServicio


class AuditoriaController:

    @staticmethod
    def obtener_auditorias():
        return AuditoriaServicio.listar_auditorias()

    @staticmethod
    def obtener_auditoria(id_auditoria):
        return AuditoriaServicio.obtener_auditoria(id_auditoria)
