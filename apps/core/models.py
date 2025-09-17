from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings

# Programa Nacional de Formación (PNF)
class PNF(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    modalidad = models.CharField(max_length=50)
    sede = models.CharField(max_length=50)
    trayectos = models.PositiveSmallIntegerField(default=4)
    duracion = models.CharField(max_length=20, default='3 años')
    estado = models.CharField(max_length=30, default='Activo')
    coordinador = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='pnf_coordinados'
    )

    def __str__(self):
        return f"{self.nombre} ({self.sede})"

# Trayecto y Tramo
class Trayecto(models.Model):
    pnf = models.ForeignKey(PNF, on_delete=models.CASCADE)
    numero = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pnf.nombre} - Trayecto {self.numero}"

class Tramo(models.Model):
    trayecto = models.ForeignKey(Trayecto, on_delete=models.CASCADE)
    numero = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.trayecto} - Tramo {self.numero}"

# Materia / Unidad Curricular
class Materia(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)
    pnf = models.ForeignKey(PNF, on_delete=models.CASCADE)
    trayecto = models.ForeignKey(Trayecto, on_delete=models.SET_NULL, null=True)
    creditos = models.PositiveSmallIntegerField(default=4)
    horas_semanales = models.PositiveSmallIntegerField(default=6)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# Sección
class Seccion(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=20)
    periodo = models.CharField(max_length=20)
    aula = models.CharField(max_length=20, blank=True)
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='secciones_docente'
    )

    def __str__(self):
        return f"{self.materia.nombre} - Sección {self.nombre} ({self.periodo})"

# Inscripción de estudiante en sección
class Inscripcion(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscripciones')
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('retirado', 'Retirado'),
        ('pendiente', 'Pendiente'),
    ], default='activo')

    def __str__(self):
        return f"{self.estudiante} en {self.seccion}"

# Calificación
class Calificacion(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    evaluacion = models.CharField(max_length=30)  # Ej: 'Eval 1', 'Eval 2', 'Final'
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscripcion} - {self.evaluacion}: {self.nota}"

# Horario de clase
class Horario(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)  # Ej: 'Lunes'
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.seccion} - {self.dia} {self.hora_inicio}-{self.hora_fin}"

# Solicitud de constancia/documento
class SolicitudConstancia(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=[
        ('constancia_estudio', 'Constancia de Estudio'),
        ('constancia_notas', 'Constancia de Notas'),
        ('constancia_regularidad', 'Constancia de Regularidad'),
    ])
    observaciones = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('procesada', 'Procesada'),
        ('rechazada', 'Rechazada'),
    ], default='pendiente')
    documento = models.FileField(upload_to='constancias/', null=True, blank=True)

    def __str__(self):
        return f"{self.estudiante} - {self.tipo} ({self.estado})"

# Reporte académico (para estadísticas, constancias, etc)
class Reporte(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # Ej: 'constancia_estudio', 'notas', 'reporte_riesgo'
    periodo = models.CharField(max_length=20)
    fecha_generado = models.DateTimeField(auto_now_add=True)
    datos = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.usuario} ({self.periodo})"

# Actividad reciente (para mostrar en portales)
class Actividad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30)  # Ej: 'calificacion', 'inscripcion', 'constancia'
    descripcion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    extra = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario} - {self.tipo} ({self.fecha})"

# Notificación
class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=[
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
    ], default='info')
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.tipo}"

# Solicitud de cambio de sección
class SolicitudCambioSeccion(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seccion_origen = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='cambios_origen')
    seccion_destino = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='cambios_destino')
    motivo = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ], default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante} {self.seccion_origen} → {self.seccion_destino} ({self.estado})"

# Asignación docente a materia/sección
class AsignacionDocente(models.Model):
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asignaciones_docente')
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    horas = models.PositiveSmallIntegerField(default=0)
    periodo = models.CharField(max_length=20)
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.docente} - {self.seccion} ({self.periodo})"

# Asistencia de estudiantes
class Asistencia(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    fecha = models.DateField()
    presente = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.inscripcion} - {self.fecha} ({'Presente' if self.presente else 'Ausente'})"

# Configuración de usuario (preferencias de portal)
class ConfiguracionUsuario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_notifications = models.CharField(max_length=20, choices=[
        ('all', 'Todas'),
        ('important', 'Solo importantes'),
        ('none', 'Desactivar'),
    ], default='all')
    report_frequency = models.CharField(max_length=10, choices=[
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
    ], default='weekly')
    default_dashboard = models.CharField(max_length=20, choices=[
        ('overview', 'Resumen general'),
        ('students', 'Monitoreo estudiantil'),
        ('teachers', 'Gestión docente'),
        ('reports', 'Reportes'),
    ], default='overview')
    language = models.CharField(max_length=5, choices=[
        ('es', 'Español'),
        ('en', 'Inglés'),
    ], default='es')
    dual_role = models.BooleanField(default=False)

    def __str__(self):
        return f"Config {self.usuario}"

# Período Académico
class PeriodoAcademico(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del Período')
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de Fin')
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ], default='inactivo')

    def __str__(self):
        return self.nombre

# Evento
class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    lugar = models.CharField(max_length=100, blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

# Foro
class Foro(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class ComentarioForo(models.Model):
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.foro}"

# Historial Académico
class HistorialAcademico(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    periodo = models.CharField(max_length=20)
    materias_aprobadas = models.PositiveIntegerField(default=0)
    materias_reprobadas = models.PositiveIntegerField(default=0)
    promedio = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.estudiante} - {self.periodo}"

# Puedes agregar más modelos según necesidades específicas del flujo administrativo.