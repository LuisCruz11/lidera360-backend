class TipoTallerDTO:

    def __init__(self, id_tipo_taller, nombre):
        self.id_tipo_taller = id_tipo_taller
        self.nombre = nombre

    def to_dict(self):
        return {
            "id_tipo_taller": self.id_tipo_taller,
            "nombre": self.nombre
        }
