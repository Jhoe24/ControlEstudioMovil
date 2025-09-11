from django import forms
from .models import Usuario, PNF

class RegistroForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de Nacimiento', required=True
    )
    pnf = forms.ModelChoiceField(queryset=PNF.objects.all(), label='Oferta Académica Disponibles', required=True)
    class Meta:
        model = Usuario
        required = True
        fields = ['cedula', 'nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'usuario', 'pnf']

class LoginForm(forms.Form):
    usuario = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Cédula o nombre de usuario '})
    )
    clave = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'})
    )