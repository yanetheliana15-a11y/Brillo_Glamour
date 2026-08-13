from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Servicio, Reserva


def inicio(request):
    servicios = Servicio.objects.all()

    return render(request, 'core/inicio.html', {
        'servicios': servicios
    })

@login_required
def reservar(request):
    servicios = Servicio.objects.all()

    if request.method == 'POST':

        cliente = request.POST.get('cliente')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        servicio = Servicio.objects.get(id=servicio_id)

        Reserva.objects.create(
            usuario=request.user,
            cliente=cliente,
            servicio=servicio,
            fecha=fecha,
            hora=hora
        )

        return redirect('inicio')

    return render(request, 'core/reservar.html', {
        'servicios': servicios
    })


def registro(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('inicio')

    return render(request, 'core/registro.html')


def iniciar_sesion(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('inicio')

    return render(request, 'core/login.html')