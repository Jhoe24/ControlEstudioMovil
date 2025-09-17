from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import (
    login_view, registro_view, registration_success, jefe_panel, estudiante_portal,
    docente_portal, coodinador_panel, administrativo_panel, error_404_view,
    error_500_view, aceptar_estudiante, exportar_verificados
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', login_view, name='logout'),
    path('register/', registro_view, name='register'),
    path('registro-exitoso/', registration_success, name='registration_success'),
    path('estudiante/portal/', estudiante_portal, name='portal_estudiantil'),
    path('docente/portal/', docente_portal, name='portal_docente'),
    path('coordinador/panel/', coodinador_panel, name='panel_coordinador'),
    path('administrativo/panel/', administrativo_panel, name='panel_administrativo'),
    path('administrativo/aceptar/<int:estudiante_id>/', aceptar_estudiante, name='aceptar_estudiante'),
    path('jefe/panel/', jefe_panel, name='panel_control_estudio'),
    path('error/404/', error_404_view, name='error_404'),
    path('error/500/', error_500_view, name='error_500'),
    path('exportar_verificados/', exportar_verificados, name='exportar_verificados'),
]

handler404 = 'apps.authentication.views.error_404_view'
handler500 = 'apps.authentication.views.error_500_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
