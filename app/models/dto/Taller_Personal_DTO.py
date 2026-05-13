class TallerPersonalDTO:

    def __init__(self, id_taller_personal, id_taller, cedula_personal, id_rol):
        self.id_taller_personal = id_taller_personal
        self.id_taller = id_taller
        self.cedula_personal = cedula_personal
        self.id_rol = id_rol

    def to_dict(self):
        return {
            "id_taller_personal": self.id_taller_personal,
            "id_taller": self.id_taller,
            "cedula_personal": self.cedula_personal,
            "id_rol": self.id_rol
        }
