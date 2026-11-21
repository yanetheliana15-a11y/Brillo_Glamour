
from django.db import models
from django.contrib.auth.models import User



class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Reserva(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        CONFIRMADA = 'Confirmada', 'Confirmada'
        RECHAZADA = 'Rechazada', 'Rechazada'
        CANCELADA = 'Cancelada', 'Cancelada'

    usuario = models.ForeignKey(
    User,
    on_delete=models.PROTECT,
    related_name='reservas'
)
    
    cliente = models.CharField(max_length=100)

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='reservas'
    )

    fecha = models.DateField()
    hora = models.TimeField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.fecha}"
