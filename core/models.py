from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    cliente = models.CharField(max_length=100)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, default="Pendiente")

    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.fecha}"