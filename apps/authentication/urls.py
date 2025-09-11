from django.urls import path
from .views import login_view, registro_view, registration_success, jefe_panel, estudiante_portal, docente_portal, coodinador_panel, administrativo_panel
from .views import error_404_view, error_500_view
urlpatterns = [
    path('', login_view, name='login_root'),  # /auth/ muestra el login
    path('login/', login_view, name='login'),
    path('logout/', login_view, name='logout'),  # /auth/logout/ cierra sesión
    path('register/', registro_view, name='register'),  # /auth/register/ muestra el registro
    path('registro-exitoso/', registration_success, name='registration_success'),
    
    path('estudiante/portal/', estudiante_portal, name='portal_estudiantil'),  # Nuevo endpoint para el portal estudiantil
    
    path('docente/portal/', docente_portal, name='portal_docente'),  # Nuevo endpoint para el portal docente
    
    path('coordinador/panel/', coodinador_panel, name='panel_coordinador'),  # Nuevo endpoint para el panel del coordinador
    
    path('administrativo/panel/', administrativo_panel, name='panel_administrativo'),  # Nuevo endpoint para el panel del personal administrativo
    
    path('jefe/panel/', jefe_panel, name='panel_control_estudio'),  # Nuevo endpoint para el panel del jefe de control de estudios

    path('error/404/', error_404_view, name='error_404'),  # Ruta para probar la página 404
    path('error/500/', error_500_view, name='error_500'),  # Ruta
]

handler404 = 'apps.authentication.views.error_404_view'
handler500 = 'apps.authentication.views.error_500_view'