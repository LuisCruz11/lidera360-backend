from app.models.dao.Auditoria_DAO import AuditoriaDAO


class AuditoriaServicio:

    @staticmethod
    def listar_auditorias():
        return AuditoriaDAO.obtener_todos()

    @staticmethod
    def obtener_auditoria(id_auditoria):
        auditoria = AuditoriaDAO.obtener_por_id(id_auditoria)
        if auditoria:
            return auditoria.to_dict()
        return None
