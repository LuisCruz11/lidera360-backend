from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dto.Progreso_Cliente_DTO import ProgresoClienteDTO


class ProgresoClienteServicio:

    @staticmethod
    def listar_progresos():
        progresos = ProgresoClienteDAO.obtener_todos()
        return [progreso.to_dict() for progreso in progresos]

    @staticmethod
    def obtener_progreso(id_progreso):
        progreso = ProgresoClienteDAO.obtener_por_id(id_progreso)
        if progreso:
            return progreso.to_dict()
        return None

    @staticmethod
    def obtener_progreso_por_cliente(cliente_cedula):
        progreso = ProgresoClienteDAO.obtener_por_cliente(cliente_cedula)
        if progreso:
            return progreso.to_dict()
        return None

    @staticmethod
    def crear_progreso(data):
        progreso = ProgresoClienteDTO(
            None,
            data.get('cliente_cedula'),
            data.get('id_tipo_taller')
        )
        return ProgresoClienteDAO.crear(progreso)

    @staticmethod
    def actualizar_progreso(id_progreso, data):
        progreso = ProgresoClienteDTO(
            id_progreso,
            data.get('cliente_cedula'),
            data.get('id_tipo_taller')
        )
        return ProgresoClienteDAO.actualizar(id_progreso, progreso)

    @staticmethod
    def eliminar_progreso(id_progreso):
        return ProgresoClienteDAO.eliminar(id_progreso)
