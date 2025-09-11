from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Usuario
from .forms import RegistroForm, LoginForm
import random, string

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

def generar_contraseña_aleatoria(longitud=8):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña

def registro_view(request):
    form = RegistroForm(request.POST or None)
    if request.method == 'POST':
        try:
            cedula = request.POST['cedula']
            nombre = request.POST['nombre']
            apellido = request.POST['apellido']
            email = request.POST['email']
            telefono = request.POST['telefono']
            fecha_nacimiento = request.POST['fecha_nacimiento']
            usuario = request.POST['usuario']
            pnf = request.POST['pnf']

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
            user.is_active = False
            user.rol = 'estudiante'
            user.save()
            messages.success(request, 'Registro completado exitosamente')
            return redirect('registration_success')
        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
    return render(request, 'auth/register.html', {'form': form})

def registration_success(request):
    return render(request, 'auth/postRegister.html')

def estudiante_portal(request):
    return render(request, 'estudiante/portal.html')

def docente_portal(request):
    return render(request, 'docente/portal.html')

def coodinador_panel(request):
    return render(request, 'coordinador/panel.html')

def administrativo_panel(request):
    return render(request, 'administrativo/panel.html')

def jefe_panel(request):
    return render(request, 'control_estudio/panel.html')