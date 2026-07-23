from django.db import models

ESTADO_CHOICES = [
        ('NUEVO', 'Nuevo'),
        ('CONTACTADO', 'Contactado'),
        ('NEGOCIACION', 'Negociacion'),
        ('GANADO','Ganado'), ('PERDIDO', 'Perdido')
    ]

class Vendedor(models.Model):
    n_empleado = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f'Numero empleado: {self.n_empleado} Nombre: {self.nombre}'


class Lead(models.Model):

    PRIORIDAD_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja')
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    presupuesto_estimado = models.DecimalField(max_digits=10, decimal_places=2)
    estado_actual = models.CharField(max_length=100, choices=ESTADO_CHOICES, default="NUEVO")
    es_corporativo = models.BooleanField(default=False)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES)
    fecha_actualizacion= models.DateTimeField(auto_now=True)
    vendedor = models.ForeignKey (Vendedor, related_name='leads', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'Nombre: {self.nombre} {self.apellido} Correo: {self.correo} Presupuesto estimado: {self.presupuesto_estimado}'

class Bitacora(models.Model):

    estado_anterior = models.CharField(max_length=100, choices=ESTADO_CHOICES)
    estado_nuevo = models.CharField(max_length=100)
    notas = models.TextField(blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    lead = models.ForeignKey(Lead, related_name='bitacora', on_delete=models.PROTECT, null=True, blank=True)
    vendedor = models.ForeignKey (Vendedor, related_name='bitacora', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self) -> str:
        return f'ID Lead: {self.lead} ID Vendedor {self.vendedor} Estado anterior: {self.estado_anterior} Nuevo estado: {self.estado_nuevo}, Notas: {self.notas}'


