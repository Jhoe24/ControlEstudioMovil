from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import login_view  # importa la vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('', login_view, name='home'),  # la raíz muestra el login
    
]

