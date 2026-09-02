class AuditoriaDTO:

    def __init__(self, id_auditoria, id_usuario, tabla, accion, descripcion, fecha, id_taller=None):
        self.id_auditoria = id_auditoria
        self.id_usuario = id_usuario
        self.tabla = tabla
        self.accion = accion
        self.descripcion = descripcion
        self.fecha = fecha
        self.id_taller = id_taller

    def to_dict(self):
        return {
            "id_auditoria": self.id_auditoria,
            "id_usuario": self.id_usuario,
            "tabla": self.tabla,
            "accion": self.accion,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "id_taller": self.id_taller
        }
