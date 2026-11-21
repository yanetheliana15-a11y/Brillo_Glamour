
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Reserva, Servicio


class ReservaForm(forms.ModelForm):

    class Meta:
        model = Reserva
        fields = ['cliente', 'servicio', 'fecha', 'hora']

        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'hora': forms.TimeInput(
                attrs={'type': 'time'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        servicios_activos = Servicio.objects.filter(activo=True)

        if self.instance.pk and self.instance.servicio_id:
            self.fields['servicio'].queryset = (
                servicios_activos |
                Servicio.objects.filter(
                    pk=self.instance.servicio_id
                )
            )
        else:
            self.fields['servicio'].queryset = servicios_activos

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].strip()

        if not cliente:
            raise forms.ValidationError(
                'Debes ingresar el nombre del cliente.'
            )

        return cliente

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < timezone.localdate():
            raise forms.ValidationError(
                'No puedes reservar en una fecha pasada.'
            )

        return fecha

    def clean_hora(self):
        hora = self.cleaned_data['hora']

        if self.cleaned_data.get('fecha') == timezone.localdate():
            ahora = timezone.localtime().time()

            if hora <= ahora:
                raise forms.ValidationError(
                    'Debes seleccionar una hora futura.'
                )

        return hora

    def clean(self):
        cleaned_data = super().clean()

        servicio = cleaned_data.get('servicio')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if not servicio or not fecha or not hora:
            return cleaned_data

        
        if (
            not self.instance.pk
            or servicio.pk != self.instance.servicio_id
        ):
            if not Servicio.objects.filter(
                pk=servicio.pk,
                activo=True
            ).exists():
                self.add_error(
                    'servicio',
                    'Este servicio ya no está disponible.'
                )
                return cleaned_data

        
        inicio = datetime.combine(fecha, hora)
        fin = inicio + timedelta(minutes=servicio.duracion)

        
        reservas = Reserva.objects.filter(
            fecha=fecha,
            servicio=servicio,
            estado__in=[
                Reserva.Estado.PENDIENTE,
                Reserva.Estado.CONFIRMADA
            ]
        ).exclude(
            pk=self.instance.pk
        )

        
        for reserva in reservas:
            inicio_existente = datetime.combine(
                reserva.fecha,
                reserva.hora
            )

            fin_existente = inicio_existente + timedelta(
                minutes=reserva.servicio.duracion
            )

            if inicio < fin_existente and fin > inicio_existente:
                raise forms.ValidationError(
                    'El servicio seleccionado ya está ocupado '
                    'en ese horario. Por favor, elige otra hora.'
                )

        return cleaned_data
