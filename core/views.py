from django.shortcuts import render
from .models import Servicio


def inicio(request):
    servicios = Servicio.objects.all()

    return render(request, 'core/inicio.html', {
        'servicios': servicios
    })