from app.models.dao.Auditoria_DAO import AuditoriaDAO
from app.models.dto.Auditoria_DTO import AuditoriaDTO


class AuditoriaServicio:

    @staticmethod
    def listar_auditorias():
        auditorias = AuditoriaDAO.obtener_todos()
        return [auditoria.to_dict() for auditoria in auditorias]

    @staticmethod
    def obtener_auditoria(id_auditoria):
        auditoria = AuditoriaDAO.obtener_por_id(id_auditoria)
        if auditoria:
            return auditoria.to_dict()
        return None

    @staticmethod
    def crear_auditoria(data):
        auditoria = AuditoriaDTO(
            None,
            data.get('id_usuario'),
            data.get('tabla'),
            data.get('accion'),
            data.get('descripcion'),
            None
        ) 
        return AuditoriaDAO.crear(auditoria)

    @staticmethod
    def actualizar_auditoria(id_auditoria, data):
        auditoria = AuditoriaDTO(
            id_auditoria,
            data.get('id_usuario'),
            data.get('tabla'),
            data.get('accion'),
            data.get('descripcion'),
            None
        )
        return AuditoriaDAO.actualizar(id_auditoria, auditoria)

    @staticmethod
    def eliminar_auditoria(id_auditoria):
        return AuditoriaDAO.eliminar(id_auditoria)
