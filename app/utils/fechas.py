from datetime import datetime, timedelta, timezone

# Colombia no usa horario de verano: UTC-5 todo el año. Render y la base de datos corren en UTC,
# así que "hoy" se calcula en esta zona para que Python y MySQL coincidan en el día.
HORA_COLOMBIA = timezone(timedelta(hours=-5))


def ahora():
    return datetime.now(HORA_COLOMBIA)


def hoy():
    return ahora().date()
