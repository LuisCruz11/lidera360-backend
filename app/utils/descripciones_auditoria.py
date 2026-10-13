# Textos de auditoría de las acciones del coordinador. Cada función recibe el contexto
# que arma @auditar (c.ruta, c.datos, c.previo, c.respuesta, c.parametros).
from app.models.dao.Cliente_DAO import ClienteDAO
from app.models.dao.Estado_DAO import EstadoDAO
from app.models.dao.Inscripcion_DAO import InscripcionDAO
from app.models.dao.Personal_DAO import PersonalDAO
from app.models.dao.Progreso_Cliente_DAO import ProgresoClienteDAO
from app.models.dao.Rol_DAO import RolDAO
from app.models.dao.Taller_DAO import TallerDAO
from app.models.dao.Taller_Personal_DAO import TallerPersonalDAO
from app.models.dao.Tipo_Taller_DAO import TipoTallerDAO
from app.models.dao.Usuario_DAO import UsuarioDAO
from app.utils.auditoria import nombre_persona


def _nombre(dao, identificador, campo="nombre"):
    registro = dao.obtener_por_id(identificador) if identificador not in (None, "") else None
    return getattr(registro, campo, None) or f"#{identificador}"


def _estado(id_estado):
    return _nombre(EstadoDAO, id_estado)


def _taller(id_taller):
    return _nombre(TallerDAO, id_taller)


def _nivel(id_tipo_taller):
    return _nombre(TipoTallerDAO, id_tipo_taller)


def _rol(id_rol):
    return _nombre(RolDAO, id_rol)


def _con_nombre(cedula, nombre):
    return f"{cedula} - {nombre}" if nombre else str(cedula)


# ---------- Clientes ----------

def cliente_creado(c):
    return f"Creó el cliente {_con_nombre(c.datos.get('cedula'), nombre_persona(c.datos))}"


def cliente_actualizado(c):
    detalle = f"estado: {_estado(c.datos.get('id_estado'))}"
    if c.datos.get("id_tipo_taller"):
        detalle += f", nivel: {_nivel(c.datos.get('id_tipo_taller'))}"
    return f"Actualizó el cliente {_con_nombre(c.ruta['cedula'], nombre_persona(c.datos))} ({detalle})"


def antes_de_eliminar_cliente(cedula):
    return {"nombre": nombre_persona(ClienteDAO.obtener_por_cedula(cedula))}


def cliente_eliminado(c):
    return f"Eliminó el cliente {_con_nombre(c.ruta['cedula'], c.previo.get('nombre'))}"


# ---------- Talleres ----------

def _resumen_taller(datos):
    return (f"{datos.get('nombre')} (nivel: {_nivel(datos.get('id_tipo_taller'))}, "
            f"del {datos.get('fecha_inicio')} al {datos.get('fecha_fin')}, estado: {_estado(datos.get('id_estado'))})")


def _personal_asignado(datos):
    if "personal_asignado" not in datos:
        return ""
    asignaciones = [
        f"{a.get('rol_en_taller')}: {nombre_persona(PersonalDAO.obtener_por_cedula(a.get('cedula_personal'))) or a.get('cedula_personal')}"
        for a in datos.get("personal_asignado") or []
        if a.get("cedula_personal")
    ]
    return f". Personal: {', '.join(asignaciones) if asignaciones else 'sin asignar'}"


def taller_creado(c):
    return f"Creó el taller {_resumen_taller(c.datos)}{_personal_asignado(c.datos)}"


def id_taller_creado(c):
    return c.respuesta.get("id_taller")


def taller_actualizado(c):
    return f"Actualizó el taller {_resumen_taller(c.datos)}{_personal_asignado(c.datos)}"


def id_taller_de_la_ruta(c):
    return c.ruta.get("id_taller")


def antes_de_eliminar_taller(id_taller):
    return {"nombre": _taller(id_taller)}


def taller_eliminado(c):
    return f"Eliminó el taller {c.previo.get('nombre')} (id {c.ruta['id_taller']}) con sus inscripciones y asignaciones"


# ---------- Personal ----------

def personal_creado(c):
    usuario = f", usuario: {c.datos.get('username')}" if c.datos.get("username") else ""
    return (f"Creó el personal {_con_nombre(c.datos.get('cedula'), nombre_persona(c.datos))} "
            f"(rol: {_rol(c.datos.get('id_rol'))}{usuario})")


def personal_actualizado(c):
    return (f"Actualizó el personal {_con_nombre(c.ruta['cedula'], nombre_persona(c.datos))} "
            f"(rol: {_rol(c.datos.get('id_rol'))})")


def antes_de_eliminar_personal(cedula):
    return {"nombre": nombre_persona(PersonalDAO.obtener_por_cedula(cedula))}


def personal_eliminado(c):
    return f"Eliminó el personal {_con_nombre(c.ruta['cedula'], c.previo.get('nombre'))} y su cuenta de usuario"


# ---------- Inscripciones ----------

def _cliente(cedula):
    return _con_nombre(cedula, nombre_persona(ClienteDAO.obtener_por_cedula(cedula)))


def _avance(c):
    nivel = c.respuesta.get("nivel_nuevo")
    return f". El cliente subió al nivel {nivel}" if nivel else ""


def inscripcion_creada(c):
    return (f"Inscribió al cliente {_cliente(c.datos.get('cliente_cedula'))} en el taller "
            f"{_taller(c.datos.get('id_taller'))} (estado: {_estado(c.datos.get('id_estado'))}){_avance(c)}")


def taller_de_los_datos(c):
    return c.datos.get("id_taller") or c.previo.get("id_taller")


def antes_de_modificar_inscripcion(id_inscripcion):
    inscripcion = InscripcionDAO.obtener_por_id(id_inscripcion)
    if not inscripcion:
        return {}
    return {"cliente_cedula": inscripcion.cliente_cedula, "id_taller": inscripcion.id_taller,
            "id_estado": inscripcion.id_estado}


def inscripcion_actualizada(c):
    cedula = c.datos.get("cliente_cedula") or c.previo.get("cliente_cedula")
    id_taller = c.datos.get("id_taller") or c.previo.get("id_taller")
    cambio = f"{_estado(c.previo.get('id_estado'))} → {_estado(c.datos.get('id_estado'))}"
    return (f"Actualizó la inscripción #{c.ruta['id_inscripcion']} del cliente {_cliente(cedula)} "
            f"en el taller {_taller(id_taller)} (estado: {cambio}){_avance(c)}")


def inscripcion_eliminada(c):
    return (f"Eliminó la inscripción #{c.ruta['id_inscripcion']} del cliente {_cliente(c.previo.get('cliente_cedula'))} "
            f"en el taller {_taller(c.previo.get('id_taller'))}")


# ---------- Usuarios ----------

def antes_de_modificar_usuario(id_usuario):
    usuario = UsuarioDAO.obtener_por_id(id_usuario)
    return {"username": usuario.username if usuario else None}


def usuario_actualizado(c):
    cambios = []
    if "username" in c.datos:
        cambios.append(f"usuario: {c.datos['username']}")
    if "activo" in c.datos:
        cambios.append("activo" if c.datos["activo"] else "inactivo")
    if "id_rol" in c.datos:
        cambios.append(f"rol: {_rol(c.datos['id_rol'])}")
    detalle = f" ({', '.join(cambios)})" if cambios else ""
    return f"Actualizó la cuenta de usuario {c.previo.get('username') or c.ruta['id_usuario']}{detalle}"


def usuario_eliminado(c):
    return f"Eliminó la cuenta de usuario {c.previo.get('username') or c.ruta['id_usuario']}"


# ---------- Catálogos: estados, roles y niveles ----------

def catalogo_creado(nombre_catalogo):
    return lambda c: f"Creó el {nombre_catalogo} {c.datos.get('nombre')}"


def catalogo_actualizado(nombre_catalogo, parametro):
    return lambda c: f"Actualizó el {nombre_catalogo} #{c.ruta[parametro]} a {c.datos.get('nombre')}"


def antes_de_eliminar_catalogo(dao, parametro):
    return lambda **ruta: {"nombre": _nombre(dao, ruta[parametro])}


def catalogo_eliminado(nombre_catalogo, parametro):
    return lambda c: f"Eliminó el {nombre_catalogo} {c.previo.get('nombre')} (#{c.ruta[parametro]})"


# ---------- Progreso y asignaciones directas ----------

def progreso_guardado(c):
    return f"Asignó el nivel {_nivel(c.datos.get('id_tipo_taller'))} al cliente {_cliente(c.datos.get('cliente_cedula'))}"


def antes_de_eliminar_progreso(id_progreso):
    progreso = ProgresoClienteDAO.obtener_por_id(id_progreso)
    return {"cliente_cedula": progreso.cliente_cedula if progreso else None}


def progreso_eliminado(c):
    return f"Eliminó el progreso #{c.ruta['id_progreso']} del cliente {_cliente(c.previo.get('cliente_cedula'))}"


def asignacion_guardada(c):
    persona = nombre_persona(PersonalDAO.obtener_por_cedula(c.datos.get("cedula_personal"))) or c.datos.get("cedula_personal")
    return f"Asignó a {persona} como {c.datos.get('rol_en_taller')} en el taller {_taller(c.datos.get('id_taller'))}"


def antes_de_eliminar_asignacion(id_taller_personal):
    asignacion = TallerPersonalDAO.obtener_por_id(id_taller_personal)
    if not asignacion:
        return {}
    return {"id_taller": asignacion.id_taller, "cedula_personal": asignacion.cedula_personal,
            "rol_en_taller": asignacion.rol_en_taller}


def asignacion_eliminada(c):
    persona = nombre_persona(PersonalDAO.obtener_por_cedula(c.previo.get("cedula_personal"))) or c.previo.get("cedula_personal")
    return f"Quitó a {persona} ({c.previo.get('rol_en_taller')}) del taller {_taller(c.previo.get('id_taller'))}"


# ---------- Reportes ----------

NOMBRES_REPORTE = {
    "clientes": "Clientes y progreso",
    "inscripciones": "Inscripciones",
    "talleres": "Talleres",
    "asistencia": "Asistencia",
    "auditoria": "Auditoría",
}


def reporte_generado(c):
    filtros = []
    if c.parametros.get("fecha_desde"):
        filtros.append(f"desde {c.parametros['fecha_desde']}")
    if c.parametros.get("fecha_hasta"):
        filtros.append(f"hasta {c.parametros['fecha_hasta']}")
    if c.parametros.get("id_taller"):
        filtros.append(f"taller: {_taller(c.parametros['id_taller'])}")
    detalle = f" (filtros: {', '.join(filtros)})" if filtros else ""
    tipo = c.ruta["tipo"]
    return f"Generó el reporte {NOMBRES_REPORTE.get(tipo, tipo)}{detalle}"
