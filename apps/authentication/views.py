from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Usuario
from .forms import RegistroForm, LoginForm
import random, string
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import sqlite3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def rol_requerido(roles_permitidos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles_permitidos:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = request.POST['usuario']
        clave = request.POST['clave']
        try:
            user = authenticate(request, username=usuario, password=clave)
            if user is not None:
                login(request, user)
                # Redirección según el rol
                if user.rol == 'estudiante':
                    return redirect('portal_estudiantil')
                elif user.rol == 'docente':
                    return redirect('portal_docente')
                elif user.rol == 'coordinador':
                    return redirect('panel_coordinador')
                elif user.rol == 'personal':
                    return redirect('panel_administrativo')
                elif user.rol == 'jefe':
                    return redirect('panel_control_estudio')
                else:
                    messages.error(request, 'Usuario no reconocido.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        except Exception as e:
            messages.error(request, f'Error al iniciar sesión: {str(e)}')
    return render(request, 'auth/login.html', {'form': form})

def generar_contraseña_aleatoria():
    letras = string.ascii_uppercase
    grupo1 = ''.join(random.choices(letras, k=4))
    grupo2 = ''.join(random.choices(letras, k=4))
    return f"{grupo1} {grupo2}"

def registro_view(request):
    form = RegistroForm(request.POST or None)
    show_modal = False
    usuario_existente = None
    pnf_actual_nombre = None
    pnf_nuevo_nombre = None

    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        usuario = request.POST.get('usuario')
        pnf = request.POST.get('pnf')

        # Buscar usuario por cédula o username
        usuario_existente = Usuario.objects.filter(cedula=cedula).first() or Usuario.objects.filter(username=usuario).first()

        if usuario_existente:
            show_modal = True
            if usuario_existente.pnf:
                pnf_actual_nombre = str(usuario_existente.pnf)
            if pnf:
                from .models import PNF
                try:
                    pnf_nuevo_nombre = str(PNF.objects.get(pk=pnf))
                except:
                    pnf_nuevo_nombre = None
                
            # Si viene confirmación de cambiar PNF
            if request.POST.get('confirmar_cambio_pnf') == '1':
                usuario_existente.pnf_id = pnf
                usuario_existente.save()
                request.session['usuario_registrado'] = {
                    'nombre': usuario_existente.nombre,
                    'apellido': usuario_existente.apellido,
                    'cedula': usuario_existente.cedula,
                    'email': usuario_existente.email,
                    'telefono': usuario_existente.telefono,
                    'pnf_nombre': str(usuario_existente.pnf) if usuario_existente.pnf else '',
                    'fecha_oferta': timezone.now().strftime('%d/%m/%Y'),
                }
                messages.success(request, 'Oferta académica actualizada exitosamente')
                return redirect('registration_success')
        else:
            try:
                nombre = request.POST['nombre']
                apellido = request.POST['apellido']
                email = request.POST['email']
                telefono = request.POST['telefono']
                fecha_nacimiento = request.POST['fecha_nacimiento']

                clave_aleatoria = generar_contraseña_aleatoria()
                user = Usuario.objects.create_user(
                    username=usuario,
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    cedula=cedula,
                    telefono=telefono,
                    fecha_nacimiento=fecha_nacimiento,
                    pnf_id=pnf
                )
                user.set_password(clave_aleatoria)
                user.clave_visible = clave_aleatoria
                user.is_active = False
                user.rol = 'estudiante'
                user.save()
                
                request.session['usuario_registrado'] = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'cedula': cedula,
                    'email': email,
                    'telefono': telefono,
                    'pnf_nombre': str(user.pnf) if user.pnf else '',
                    'fecha_oferta':  timezone.now().strftime('%d/%m/%Y'),
                }
                    
                messages.success(request, 'Registro completado exitosamente')
                return redirect('registration_success')
            except Exception as e:
                messages.error(request, f'Error al registrar usuario: {str(e)}')
    return render(request, 'auth/register.html', {
        'form': form, 
        'show_modal': show_modal, 
        'usuario_existente': usuario_existente,
        'pnf_actual_nombre': pnf_actual_nombre,
        'pnf_nuevo_nombre': pnf_nuevo_nombre})

def registration_success(request):
    datos = {}
    pnf_nombre = None
    fecha_oferta = None

    if request.user.is_authenticated:
        usuario = request.user
        datos = {
            'nombre': getattr(usuario, 'nombre', getattr(usuario, 'first_name', '')),
            'apellido': getattr(usuario, 'apellido', getattr(usuario, 'last_name', '')),
            'cedula': getattr(usuario, 'cedula', ''),
            'email': getattr(usuario, 'email', ''),
            'telefono': getattr(usuario, 'telefono', ''),
        }
        if hasattr(usuario, 'pnf') and usuario.pnf:
            pnf_nombre = str(usuario.pnf)
        fecha_oferta = usuario.date_joined.strftime('%d/%m/%Y')
    elif 'usuario_registrado' in request.session:
        usuario = request.session['usuario_registrado']
        datos = {
            'nombre': usuario.get('nombre', ''),
            'apellido': usuario.get('apellido', ''),
            'cedula': usuario.get('cedula', ''),
            'email': usuario.get('email', ''),
            'telefono': usuario.get('telefono', ''),
        }
        pnf_nombre = usuario.get('pnf_nombre')
        fecha_oferta = usuario.get('fecha_oferta')
    else:
        datos = {
            'nombre': '',
            'apellido': '',
            'cedula': '',
            'email': '',
            'telefono': '',
        }

    return render(request, 'auth/postRegister.html', {
        'datos': datos,
        'pnf_nombre': pnf_nombre,
        'fecha_oferta': fecha_oferta,
    })

@login_required
@rol_requerido(['personal'])
def administrativo_panel(request):
    estudiantes_pendientes = Usuario.objects.filter(rol='estudiante', is_active=False)
    estudiantes_verificados_list = Usuario.objects.filter(rol='estudiante', is_active=True)
    total_estudiantes = Usuario.objects.filter(rol='estudiante').count()
    estudiantes_verificados = estudiantes_verificados_list.count()
    estudiantes_pendientes_count = estudiantes_pendientes.count()
    docentes_activos = Usuario.objects.filter(rol='docente', is_active=True).count()
    coordinadores = Usuario.objects.filter(rol='coordinador', is_active=True).count()
    personal_admin = Usuario.objects.filter(rol='personal', is_active=True).count()

    # Personal académico y administrativo
    personal = Usuario.objects.filter(rol__in=['docente', 'coordinador', 'personal'])

    return render(request, 'administrativo/panel.html', {
        'estudiantes_pendientes': estudiantes_pendientes,
        'estudiantes_verificados_list': estudiantes_verificados_list,  # <--- nuevo
        'total_estudiantes': total_estudiantes,
        'estudiantes_verificados': estudiantes_verificados,
        'estudiantes_pendientes_count': estudiantes_pendientes_count,
        'docentes_activos': docentes_activos,
        'coordinadores': coordinadores,
        'personal_admin': personal_admin,
        'personal': personal,
    })

def aceptar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Usuario, id=estudiante_id, rol='estudiante', is_active=False)
    if request.method == 'POST':
        estudiante.is_active = True
        estudiante.save()
        # Renderizar el HTML del correo
        
        clave_real = estudiante.contrasena
        
        html_content = render_to_string('emails/bienvenida.html', {
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'cedula': estudiante.cedula,
            'email': estudiante.email,
            'carrera': estudiante.pnf.nombre if estudiante.pnf else '',
            'periodo': estudiante.date_joined.strftime('%Y-%m'),
            'usuario': estudiante.username,
            'clave': estudiante.clave_visible,  # O usa estudiante.password si guardas la clave original
        })
        subject = '¡Bienvenido a la Universidad!'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [estudiante.email]
        msg = EmailMultiAlternatives(subject, '', from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, f'Estudiante {estudiante.nombre} activado y notificado por correo.')
    return redirect('panel_administrativo')


@login_required
@rol_requerido(['estudiante'])
def estudiante_portal(request):
    return render(request, 'estudiante/portal.html')

@login_required
@rol_requerido(['docente'])
def docente_portal(request):
    return render(request, 'docente/portal.html')

@login_required
@rol_requerido(['coordinador'])
def coodinador_panel(request):
    return render(request, 'coordinador/panel.html')

@login_required
@rol_requerido(['jefe'])
def jefe_panel(request):
    return render(request, 'control_estudio/panel.html')


def error_404_view(request, exception):
    return render(request, 'error/404.html', status=404)

def error_500_view(request):
    return render(request, 'error/500.html', status=500)

@csrf_exempt
def exportar_verificados(request):
    if request.method == 'POST':
        # Filtra solo estudiantes verificados
        estudiantes = Usuario.objects.filter(rol='estudiante', is_active=True, verificado=True)
        # Conexión a la base de datos externa
        conn = sqlite3.connect('ruta/a/tu/archivo_externo.db')
        cursor = conn.cursor()
        # Crea la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes_verificados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                cedula TEXT,
                email TEXT,
                carrera TEXT,
                fecha_registro TEXT
            )
        ''')
        # Inserta los datos
        for est in estudiantes:
            cursor.execute('''
                INSERT INTO estudiantes_verificados (nombre, apellido, cedula, email, carrera, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                est.nombre,
                est.apellido,
                est.cedula,
                est.email,
                str(est.pnf) if est.pnf else '',
                est.date_joined.strftime('%Y-%m-%d')
            ))
        conn.commit()
        conn.close()
        return JsonResponse({'mensaje': 'Estudiantes exportados exitosamente.', 'status': 'success'})
    return JsonResponse({'mensaje': 'Método no permitido.', 'status': 'error'})



