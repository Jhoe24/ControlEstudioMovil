from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import login_view  # importa la vista
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('', login_view, name='home'),  # la raíz muestra el login
    
]
# vamos a verificar si estamos en modo debug para poder mostrar los media y los static/ statifiles

if settings.DEBUG:
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  
