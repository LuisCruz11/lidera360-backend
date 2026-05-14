from app.models.dao.Taller_DAO import TallerDAO
from app.models.dto.Taller_DTO import TallerDTO
from app.models.dao.Taller_Personal_DAO import TallerPersonalDAO
from app.models.dto.Taller_Personal_DTO import TallerPersonalDTO
from app.database.Db import Db


class TallerServicio:

    @staticmethod
    def listar_talleres():
        talleres = TallerDAO.obtener_todos()
        return [taller.to_dict() for taller in talleres]

    @staticmethod
    def obtener_taller(id_taller):
        taller = TallerDAO.obtener_por_id(id_taller)
        if taller:
            return taller.to_dict()
        return None

    @staticmethod
    def crear_taller(data):
        taller = TallerDTO(
            None,
            data['nombre'],
            data.get('id_tipo_taller'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('id_estado')
        )
        personal_asignado = data.get('personal_asignado') or []

        if not personal_asignado:
            return TallerDAO.crear(taller)

        conexion = Db.obtener_conexion()
        try:
            id_taller = TallerDAO.crear(taller, conexion)
            for asignacion in personal_asignado:
                if not asignacion.get('cedula_personal') or not asignacion.get('id_rol'):
                    continue

                TallerPersonalDAO.crear(TallerPersonalDTO(
                    None,
                    id_taller,
                    asignacion.get('cedula_personal'),
                    asignacion.get('id_rol')
                ), conexion)
            conexion.commit()
            return id_taller
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def actualizar_taller(id_taller, data):
        taller = TallerDTO(
            id_taller,
            data['nombre'],
            data.get('id_tipo_taller'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('id_estado')
        )
        return TallerDAO.actualizar(id_taller, taller)

    @staticmethod
    def eliminar_taller(id_taller):
        return TallerDAO.eliminar(id_taller)
