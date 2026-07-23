from rest_framework import serializers
from .models import Vendedor, Lead, Bitacora


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = ['id', 'n_empleado', 'nombre']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'nombre', 'apellido', 'correo', 'presupuesto_estimado', 'estado_actual', 'es_corporativo', 'prioridad', 'fecha_actualizacion', 'vendedor']

class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = ['id', 'estado_anterior', 'estado_nuevo', 'notas', 'fecha_evento', 'lead', 'vendedor']

