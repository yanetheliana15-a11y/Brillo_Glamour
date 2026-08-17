from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('fecha', 'hora')

    return render(request, 'core/mis_reservas.html', {
        'reservas': reservas
    })

@login_required
def cancelar_reserva(request, reserva_id):

    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user
    )

    if request.method == 'POST':
        reserva.estado = 'Cancelada'
        reserva.save()

    return redirect('mis_reservas')

@login_required
def editar_reserva(request, reserva_id):

    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user
    )

    if request.method == 'POST':
        reserva.fecha = request.POST.get('fecha')
        reserva.hora = request.POST.get('hora')
        reserva.save()

        return redirect('mis_reservas')

    return render(request, 'core/editar_reserva.html', {
        'reserva': reserva
    })
def api_servicios(request):

    servicios = Servicio.objects.all()

    datos = []

    for servicio in servicios:
        datos.append({
            'id': servicio.id,
            'nombre': servicio.nombre,
            'descripcion': servicio.descripcion,
            'precio': str(servicio.precio),
            'duracion': servicio.duracion
        })

    return JsonResponse(datos, safe=False)
