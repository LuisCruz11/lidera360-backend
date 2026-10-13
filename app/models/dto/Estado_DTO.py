AMBITOS_ESTADO = ("cliente", "taller", "inscripcion")


def _como_lista(aplica_a):
    if aplica_a is None:
        return list(AMBITOS_ESTADO)
    if isinstance(aplica_a, (set, frozenset, list, tuple)):
        valores = aplica_a
    else:
        valores = str(aplica_a).split(",")
    return [ambito for ambito in AMBITOS_ESTADO if ambito in {str(valor).strip() for valor in valores}]


class EstadoDTO:

    def __init__(self, id_estado, nombre, aplica_a=None):
        self.id_estado = id_estado
        self.nombre = nombre
        self.aplica_a = _como_lista(aplica_a)

    def aplica_para(self, ambito):
        return ambito in self.aplica_a

    def to_dict(self):
        return {
            "id_estado": self.id_estado,
            "nombre": self.nombre,
            "aplica_a": self.aplica_a
        }
