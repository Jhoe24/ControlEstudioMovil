from django import forms
from .models import Usuario
from apps.core.models import PNF

class RegistroForm(forms.ModelForm):
    nacionalidad = forms.ChoiceField(choices=Usuario.NACIONALIDAD_CHOICES, required=True)
    sexo = forms.ChoiceField(choices=Usuario.SEXO_CHOICES, label='Sexo', required=True)
    cedula = forms.CharField(max_length=10, label='Cédula', required=True)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de Nacimiento', required=True
    )
    pnf = forms.ModelChoiceField(queryset=PNF.objects.all(), label='Oferta Académica Disponibles', required=True)
    class Meta:
        model = Usuario
        required = True
        fields = ['nacionalidad', 'cedula', 'nombre', 'apellido', 'email', 'telefono', 'sexo', 'fecha_nacimiento', 'usuario', 'pnf']

class LoginForm(forms.Form):
    usuario = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese nombre de usuario '})
    )
    clave = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese contraseña'})
    )