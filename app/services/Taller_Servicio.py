from app.models.dao.Taller_DAO import TallerDAO
from app.models.dto.Taller_DTO import TallerDTO
from app.models.dao.Taller_Personal_DAO import TallerPersonalDAO
from app.models.dto.Taller_Personal_DTO import TallerPersonalDTO
from app.models.dao.Auditoria_DAO import AuditoriaDAO
from app.models.dto.Auditoria_DTO import AuditoriaDTO
from app.database.Db import Db


def _validar_fechas(fecha_inicio, fecha_fin):
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio")


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
    def obtener_detalle(id_taller):
        return TallerDAO.obtener_detalle(id_taller)

    @staticmethod
    def agregar_nota(id_taller, id_usuario, data):
        descripcion = (data.get('descripcion') or '').strip()
        if not descripcion:
            raise ValueError("La descripción de la nota es obligatoria")

        if not TallerDAO.obtener_por_id(id_taller):
            raise ValueError("Taller no encontrado")

        nota = AuditoriaDTO(None, id_usuario, 'taller', 'nota', descripcion, None, id_taller)
        return AuditoriaDAO.crear(nota)

    @staticmethod
    def crear_taller(data):
        _validar_fechas(data.get('fecha_inicio'), data.get('fecha_fin'))

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
                if not asignacion.get('cedula_personal') or not asignacion.get('rol_en_taller'):
                    continue

                TallerPersonalDAO.crear(TallerPersonalDTO(
                    None,
                    id_taller,
                    asignacion.get('cedula_personal'),
                    asignacion.get('rol_en_taller')
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
        _validar_fechas(data.get('fecha_inicio'), data.get('fecha_fin'))

        taller = TallerDTO(
            id_taller,
            data['nombre'],
            data.get('id_tipo_taller'),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('id_estado')
        )

        if 'personal_asignado' not in data:
            return TallerDAO.actualizar(id_taller, taller)

        conexion = Db.obtener_conexion()
        try:
            actualizado = TallerDAO.actualizar(id_taller, taller, conexion)
            TallerPersonalDAO.eliminar_por_taller(id_taller, conexion)
            for asignacion in data.get('personal_asignado') or []:
                if not asignacion.get('cedula_personal') or not asignacion.get('rol_en_taller'):
                    continue

                TallerPersonalDAO.crear(TallerPersonalDTO(
                    None,
                    id_taller,
                    asignacion.get('cedula_personal'),
                    asignacion.get('rol_en_taller')
                ), conexion)
            conexion.commit()
            return actualizado
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def eliminar_taller(id_taller):
        return TallerDAO.eliminar(id_taller)
