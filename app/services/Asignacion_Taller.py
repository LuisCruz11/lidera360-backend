from app.models.dao.Taller_DAO import TallerDAO

ROL_EN_TALLER_COACH = 'coach'
ROL_EN_TALLER_PERSONAL_CAPACITADO = 'personal capacitado'


def validar_cedula_personal(cedula_personal):
    if not cedula_personal:
        raise PermissionError("Tu usuario no está vinculado a un registro de personal")


def validar_asignacion(id_taller, cedula_personal, rol_en_taller):
    """Verifica que el taller exista y que la persona esté asignada a él con ese rol."""
    validar_cedula_personal(cedula_personal)
    if not TallerDAO.obtener_por_id(id_taller):
        raise LookupError("Taller no encontrado")
    if not TallerDAO.tiene_personal_asignado(id_taller, cedula_personal, rol_en_taller):
        raise PermissionError("No estás asignado a este taller")
