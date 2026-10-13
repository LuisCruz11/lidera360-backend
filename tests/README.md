# Pruebas automáticas del back-end

Suite de pruebas con **pytest** que verifica las reglas de negocio y los permisos de la API de Lidera360.

## Cómo ejecutarlas

Desde la carpeta `lidera360-backend`:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Qué cubren

| Archivo | Funcionalidad |
|---|---|
| `test_coach.py` | Talleres asignados, actividades y evaluación de participantes del coach |
| `test_cliente.py` | Cancelar inscripción y editar datos de contacto del cliente |
| `test_progreso.py` | Avance automático de nivel al aprobar un taller (coach y coordinador) |
| `test_personal_capacitado.py` | Talleres y participantes propios, notas y registro de asistencia |
| `test_recuperar_password.py` | Recuperación de contraseña con enlace firmado de un solo uso |
| `test_notificaciones.py` | Correos al cliente por inscripción, resultado (aprobado / no aprobado) y cancelación |
| `test_reportes.py` | Reportes en Excel del coordinador: contenido, filtros y permisos |
| `test_auditoria.py` | Auditoría de las acciones del coordinador, integridad de la tabla y hora de Colombia |
| `test_infraestructura.py` | Envío de correos por Brevo y configuración de la conexión a MySQL |

## Aislamiento

- `conftest.py` define variables de entorno ficticias antes de importar la aplicación, así que el `.env` local no se usa.
- Cualquier conexión a MySQL o petición HTTP que no esté simulada hace fallar la prueba de inmediato.
- Los accesos a datos (DAO) se reemplazan con objetos simulados (`unittest.mock`), por lo que la suite se ejecuta en pocos segundos y sin conexión a internet.
