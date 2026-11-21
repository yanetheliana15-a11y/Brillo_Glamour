
from django.contrib import admin
from .models import Servicio, Reserva
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'duracion', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo', 'duracion')
    list_editable = ('activo',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'usuario',
        'servicio',
        'fecha',
        'hora',
        'estado'
    )

    search_fields = (
        'cliente',
        'usuario__username',
        'servicio__nombre'
    )

    list_filter = ('estado', 'fecha', 'servicio')
    ordering = ('fecha', 'hora')
