class TallerDTO:

    def __init__(self, id_taller, nombre, id_tipo_taller, fecha_inicio, fecha_fin, id_estado):
        self.id_taller = id_taller
        self.nombre = nombre
        self.id_tipo_taller = id_tipo_taller
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.id_estado = id_estado

    def to_dict(self):
        return {
            "id_taller": self.id_taller,
            "nombre": self.nombre,
            "id_tipo_taller": self.id_tipo_taller,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "id_estado": self.id_estado
        }
