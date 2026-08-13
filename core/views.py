from django.shortcuts import render, redirect
from .models import Servicio, Reserva


def inicio(request):
    servicios = Servicio.objects.all()

    return render(request, 'core/inicio.html', {
        'servicios': servicios
    })


def reservar(request):
    servicios = Servicio.objects.all()

    if request.method == 'POST':

        cliente = request.POST.get('cliente')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        servicio = Servicio.objects.get(id=servicio_id)

        Reserva.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha=fecha,
            hora=hora
        )

        return redirect('inicio')

    return render(request, 'core/reservar.html', {
        'servicios': servicios
    })