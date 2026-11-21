
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Servicio, Reserva
from .forms import ReservaForm


def inicio(request):
    servicios = Servicio.objects.filter(activo=True)

    return render(request, 'core/inicio.html', {
        'servicios': servicios
    })


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'core/registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
            return render(request, 'core/registro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'core/registro.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
        return redirect('inicio')

    return render(request, 'core/registro.html')


def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect('inicio')

        messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'core/login.html')


@login_required
@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')


@login_required
def reservar(request):
    if request.method == 'POST':
        formulario = ReservaForm(request.POST)

        if formulario.is_valid():
            reserva = formulario.save(commit=False)
            reserva.usuario = request.user
            reserva.estado = Reserva.Estado.PENDIENTE
            reserva.save()

            messages.success(
                request,
                'Tu solicitud fue enviada y está pendiente de confirmación.'
            )

            return redirect('mis_reservas')
    else:
        formulario = ReservaForm()

    return render(request, 'core/reservar.html', {
        'formulario': formulario
    })


@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(
        usuario=request.user
    ).select_related('servicio').order_by('fecha', 'hora')

    return render(request, 'core/mis_reservas.html', {
        'reservas': reservas
    })


@login_required
@require_POST
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user
    )

    if reserva.estado in [
        Reserva.Estado.PENDIENTE,
        Reserva.Estado.CONFIRMADA
    ]:
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save()
        messages.success(request, 'Tu reserva ha sido cancelada.')
    else:
        messages.error(request, 'Esta reserva no se puede cancelar.')

    return redirect('mis_reservas')


@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(
        Reserva,
        id=reserva_id,
        usuario=request.user
    )

    if reserva.estado not in [
        Reserva.Estado.PENDIENTE,
        Reserva.Estado.CONFIRMADA
    ]:
        messages.error(request, 'Esta reserva no se puede modificar.')
        return redirect('mis_reservas')

    if request.method == 'POST':
        formulario = ReservaForm(request.POST, instance=reserva)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Reserva actualizada correctamente.')
            return redirect('mis_reservas')
    else:
        formulario = ReservaForm(instance=reserva)

    return render(request, 'core/editar_reserva.html', {
        'reserva': reserva,
        'formulario': formulario
    })


def es_administrador(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(es_administrador)
def administrar_reservas(request):
    reservas = Reserva.objects.select_related(
        'usuario', 'servicio'
    ).order_by('fecha', 'hora')

    return render(request, 'core/admin_reservas.html', {
        'reservas': reservas
    })


@login_required
@user_passes_test(es_administrador)
@require_POST


def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    nuevo_estado = request.POST.get('estado')

    estados_permitidos = {
        Reserva.Estado.CONFIRMADA,
        Reserva.Estado.RECHAZADA,
        Reserva.Estado.CANCELADA
    }

    if nuevo_estado not in estados_permitidos:
        messages.error(request, 'Estado de reserva no válido.')
        return redirect('administrar_reservas')

    if nuevo_estado == Reserva.Estado.CANCELADA:
        if reserva.estado != Reserva.Estado.CONFIRMADA:
            messages.error(
                request,
                'Solo puedes cancelar reservas confirmadas.'
            )
            return redirect('administrar_reservas')

    else:
        if reserva.estado != Reserva.Estado.PENDIENTE:
            messages.error(
                request,
                'Esta reserva ya no está pendiente.'
            )
            return redirect('administrar_reservas')

    reserva.estado = nuevo_estado
    reserva.save()

    messages.success(request, 'Estado de reserva actualizado.')

    return redirect('administrar_reservas')




def api_servicios(request):
    servicios = Servicio.objects.filter(activo=True)

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
