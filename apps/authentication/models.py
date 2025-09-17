from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import PNF  

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('coordinador', 'Coordinador'),
        ('personal', 'Personal Administrativo'),
        ('jefe', 'Jefe de Control de Estudios'),
    ]
    usuario = models.CharField(max_length=150, unique=True, verbose_name='Usuario', blank=True, null=True)
    contrasena = models.CharField(max_length=128, verbose_name='Contraseña', blank=True)
    clave_visible = models.CharField(max_length=10, verbose_name='Clave Visible', null=True, blank=True)

    cedula = models.CharField(max_length=12, unique=True, verbose_name='Cédula', null=True, blank=True)
    nombre = models.CharField(max_length=50, verbose_name='Nombre', null=True, blank=True)
    apellido = models.CharField(max_length=50, verbose_name='Apellido', null=True, blank=True)
    email = models.EmailField(verbose_name='Correo Electrónico', null=True, blank=True)
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', null=True, blank=True)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', null=True, blank=True)
    pnf = models.ForeignKey(PNF, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Oferta Académica')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante', verbose_name='Rol')


    def __str__(self):
        return self.usuario

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        if not self.usuario:
            self.usuario = self.username
        if not self.contrasena:
            self.contrasena = self.password
        super().save(*args, **kwargs)
        
        
        
     