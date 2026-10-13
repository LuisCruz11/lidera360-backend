from app.models.dao.Estado_DAO import EstadoDAO
from app.models.dto.Estado_DTO import AMBITOS_ESTADO, EstadoDTO

NOMBRES_AMBITO = {"cliente": "un cliente", "taller": "un taller", "inscripcion": "una inscripción"}


def _validar_ambito(ambito):
    if ambito not in AMBITOS_ESTADO:
        raise ValueError(f"aplica_a debe ser uno de: {', '.join(AMBITOS_ESTADO)}")


def _leer_aplica_a(data):
    valor = data.get('aplica_a')
    if valor in (None, "", []):
        return list(AMBITOS_ESTADO)
    valores = valor if isinstance(valor, list) else str(valor).split(",")
    valores = [str(ambito).strip() for ambito in valores]
    for ambito in valores:
        _validar_ambito(ambito)
    return valores


class EstadoServicio:

    @staticmethod
    def listar_estados(aplica_a=None):
        if aplica_a:
            _validar_ambito(aplica_a)
        return [estado.to_dict() for estado in EstadoDAO.obtener_todos(aplica_a)]

    @staticmethod
    def obtener_estado(id_estado):
        estado = EstadoDAO.obtener_por_id(id_estado)
        if estado:
            return estado.to_dict()
        return None

    @staticmethod
    def validar_estado_para(id_estado, ambito):
        estado = EstadoDAO.obtener_por_id(id_estado) if id_estado not in (None, "") else None
        if not estado:
            raise ValueError("El estado seleccionado no existe")
        if not estado.aplica_para(ambito):
            raise ValueError(f"El estado {estado.nombre} no se puede asignar a {NOMBRES_AMBITO[ambito]}")
        return estado

    @staticmethod
    def crear_estado(data):
        estado = EstadoDTO(None, data['nombre'], _leer_aplica_a(data))
        return EstadoDAO.crear(estado)

    @staticmethod
    def actualizar_estado(id_estado, data):
        estado = EstadoDTO(id_estado, data['nombre'], _leer_aplica_a(data))
        return EstadoDAO.actualizar(id_estado, estado)

    @staticmethod
    def eliminar_estado(id_estado):
        return EstadoDAO.eliminar(id_estado)
