from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import RegistroForm
from .models import Perfil

def registro_usuario(request):

    form = RegistroForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        user = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name']
        )

        Perfil.objects.create(
            user=user,
            identificacion=form.cleaned_data['identificacion']
        )

        return render(request, 'usuarios/registro_exitoso.html')

    return render(request, 'usuarios/registro.html', {'form': form})