from django import forms
from django.contrib.auth.models import User
from .models import Perfil
import re

_PASSWORD_RULES = [
    (r"[A-Z]", "Debe contener al menos una letra mayúscula"),
    (r"[a-z]", "Debe contener al menos una letra minúscula"),
    (r"\d",    "Debe contener al menos un número"),
    (r'[!@#$%^&*(),.?":{}|<>]', "Debe contener al menos un carácter especial"),
]


class RegistroForm(forms.ModelForm):

    identificacion = forms.CharField(max_length=20)

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña"
    )

    confirmar_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_first_name(self):
        nombre = self.cleaned_data['first_name']

        if not nombre.isalpha():
            raise forms.ValidationError(
                "El nombre solo debe contener letras"
            )

        return nombre

    def clean_last_name(self):
        apellido = self.cleaned_data['last_name']

        if not apellido.isalpha():
            raise forms.ValidationError(
                "El apellido solo debe contener letras"
            )

        return apellido

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Normalizar email
        email = email.lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "El correo ya está registrado"
            )

        return email

    def clean_identificacion(self):
        identificacion = self.cleaned_data['identificacion']

        if Perfil.objects.filter(identificacion=identificacion).exists():
            raise forms.ValidationError(
                "La identificación ya está registrada"
            )

        return identificacion

    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 6:
            raise forms.ValidationError(
                "La contraseña debe tener mínimo 6 caracteres"
            )

        for pattern, message in _PASSWORD_RULES:
            if not re.search(pattern, password):
                raise forms.ValidationError(message)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirmar_password")

        if password and confirmar and password != confirmar:
            raise forms.ValidationError(
                "Las contraseñas no coinciden"
            )

        return cleaned_data