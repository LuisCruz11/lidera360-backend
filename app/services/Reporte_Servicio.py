from datetime import date

from app.models.dao.Reporte_DAO import ReporteDAO
from app.models.dao.Taller_DAO import TallerDAO
from app.utils.reporte_excel import generar_excel


def _nombre_completo(fila):
    return f"{fila.get('nombres') or ''} {fila.get('apellidos') or ''}".strip()


def _proporcion(parte, total):
    return round(parte / total, 4) if total else None


def _fecha(valor, etiqueta):
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ValueError(f"La fecha {etiqueta} debe tener el formato AAAA-MM-DD")


def _id_taller(valor):
    if valor in (None, ""):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError("El taller seleccionado no es válido")


def _nombre_taller(id_taller):
    taller = TallerDAO.obtener_por_id(id_taller)
    if not taller:
        raise LookupError("Taller no encontrado")
    return taller.nombre


def _reporte_clientes(_parametros):
    filas = []
    for fila in ReporteDAO.clientes_y_progreso():
        inscripciones = int(fila["inscripciones"] or 0)
        aprobados = int(fila["aprobados"] or 0)
        no_aprobados = int(fila["no_aprobados"] or 0)
        filas.append({
            **fila,
            "nombre": _nombre_completo(fila),
            "en_curso": inscripciones - aprobados - no_aprobados,
            "programa_completado": "Sí" if fila.get("programa_completado") else "No",
        })

    columnas = [
        {"clave": "cedula", "titulo": "Cédula", "ancho": 14},
        {"clave": "nombre", "titulo": "Cliente", "ancho": 28},
        {"clave": "correo", "titulo": "Correo", "ancho": 30},
        {"clave": "telefono", "titulo": "Teléfono", "ancho": 14},
        {"clave": "edad", "titulo": "Edad", "ancho": 8, "formato": "entero"},
        {"clave": "estado", "titulo": "Estado", "ancho": 12},
        {"clave": "nivel_actual", "titulo": "Nivel actual", "ancho": 14},
        {"clave": "inscripciones", "titulo": "Inscripciones", "ancho": 14, "formato": "entero"},
        {"clave": "aprobados", "titulo": "Aprobados", "ancho": 12, "formato": "entero"},
        {"clave": "no_aprobados", "titulo": "No aprobados", "ancho": 14, "formato": "entero"},
        {"clave": "en_curso", "titulo": "En curso", "ancho": 10, "formato": "entero"},
        {"clave": "programa_completado", "titulo": "Programa completado", "ancho": 20},
    ]
    return "Clientes y progreso", columnas, filas, []


def _reporte_inscripciones(parametros):
    desde = _fecha(parametros.get("fecha_desde"), "inicial")
    hasta = _fecha(parametros.get("fecha_hasta"), "final")
    if desde and hasta and hasta < desde:
        raise ValueError("La fecha final no puede ser anterior a la fecha inicial")
    id_taller = _id_taller(parametros.get("id_taller"))

    filtros = []
    if desde:
        filtros.append(f"Desde {desde.strftime('%d/%m/%Y')}")
    if hasta:
        filtros.append(f"Hasta {hasta.strftime('%d/%m/%Y')}")
    if id_taller:
        filtros.append(f"Taller: {_nombre_taller(id_taller)}")

    filas = [
        {**fila, "cliente": _nombre_completo(fila)}
        for fila in ReporteDAO.inscripciones(desde, hasta, id_taller)
    ]
    columnas = [
        {"clave": "fecha_inscripcion", "titulo": "Fecha de inscripción", "ancho": 16, "formato": "fecha"},
        {"clave": "cedula", "titulo": "Cédula", "ancho": 14},
        {"clave": "cliente", "titulo": "Cliente", "ancho": 28},
        {"clave": "correo", "titulo": "Correo", "ancho": 30},
        {"clave": "taller", "titulo": "Taller", "ancho": 26},
        {"clave": "nivel", "titulo": "Nivel", "ancho": 12},
        {"clave": "fecha_inicio", "titulo": "Inicio del taller", "ancho": 14, "formato": "fecha"},
        {"clave": "fecha_fin", "titulo": "Fin del taller", "ancho": 14, "formato": "fecha"},
        {"clave": "coach", "titulo": "Coach", "ancho": 24},
        {"clave": "estado", "titulo": "Estado", "ancho": 14},
    ]
    return "Inscripciones", columnas, filas, filtros


def _reporte_talleres(_parametros):
    filas = []
    for fila in ReporteDAO.talleres():
        aprobados = int(fila["aprobados"] or 0)
        evaluados = aprobados + int(fila["no_aprobados"] or 0)
        filas.append({**fila, "tasa_aprobacion": _proporcion(aprobados, evaluados)})

    columnas = [
        {"clave": "nombre", "titulo": "Taller", "ancho": 26},
        {"clave": "nivel", "titulo": "Nivel", "ancho": 12},
        {"clave": "fecha_inicio", "titulo": "Inicio", "ancho": 12, "formato": "fecha"},
        {"clave": "fecha_fin", "titulo": "Fin", "ancho": 12, "formato": "fecha"},
        {"clave": "estado", "titulo": "Estado", "ancho": 12},
        {"clave": "coach", "titulo": "Coach", "ancho": 24},
        {"clave": "coordinador", "titulo": "Coordinador", "ancho": 24},
        {"clave": "personal_capacitado", "titulo": "Personal capacitado", "ancho": 28},
        {"clave": "inscritos", "titulo": "Inscritos", "ancho": 10, "formato": "entero"},
        {"clave": "aprobados", "titulo": "Aprobados", "ancho": 11, "formato": "entero"},
        {"clave": "no_aprobados", "titulo": "No aprobados", "ancho": 13, "formato": "entero"},
        {"clave": "tasa_aprobacion", "titulo": "% aprobación (de evaluados)", "ancho": 16, "formato": "porcentaje"},
    ]
    return "Talleres", columnas, filas, []


def _reporte_asistencia(parametros):
    id_taller = _id_taller(parametros.get("id_taller"))
    filtros = [f"Taller: {_nombre_taller(id_taller)}"] if id_taller else []

    filas = []
    for fila in ReporteDAO.asistencia(id_taller):
        sesiones = int(fila["sesiones"] or 0)
        asistencias = int(fila["asistencias"] or 0)
        filas.append({
            **fila,
            "participante": _nombre_completo(fila),
            "sesiones": sesiones,
            "asistencias": asistencias,
            "porcentaje": _proporcion(asistencias, sesiones),
        })

    columnas = [
        {"clave": "taller", "titulo": "Taller", "ancho": 26},
        {"clave": "fecha_inicio", "titulo": "Inicio", "ancho": 12, "formato": "fecha"},
        {"clave": "fecha_fin", "titulo": "Fin", "ancho": 12, "formato": "fecha"},
        {"clave": "cedula", "titulo": "Cédula", "ancho": 14},
        {"clave": "participante", "titulo": "Participante", "ancho": 28},
        {"clave": "estado", "titulo": "Estado", "ancho": 14},
        {"clave": "sesiones", "titulo": "Sesiones registradas", "ancho": 12, "formato": "entero"},
        {"clave": "asistencias", "titulo": "Asistencias", "ancho": 12, "formato": "entero"},
        {"clave": "porcentaje", "titulo": "% asistencia", "ancho": 12, "formato": "porcentaje"},
    ]
    return "Asistencia", columnas, filas, filtros


REPORTES = {
    "clientes": _reporte_clientes,
    "inscripciones": _reporte_inscripciones,
    "talleres": _reporte_talleres,
    "asistencia": _reporte_asistencia,
}


class ReporteServicio:

    @staticmethod
    def generar(tipo, parametros):
        """Devuelve (bytes del .xlsx, nombre de archivo) del reporte pedido."""
        construir = REPORTES.get(tipo)
        if not construir:
            raise LookupError("El reporte solicitado no existe")

        titulo, columnas, filas, filtros = construir(parametros)
        contenido = generar_excel(titulo, columnas, filas, filtros)
        nombre_archivo = f"Lidera360-{tipo}-{date.today().isoformat()}.xlsx"
        return contenido, nombre_archivo
