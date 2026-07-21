from core_engine.models import EstadoLead, TRANSICIONES
from core_engine.exceptions import EstadoInvalidoError

def validar_transicion(estado_actual, nuevo_estado):
    destinos = TRANSICIONES[estado_actual]
    if nuevo_estado not in destinos:
        raise EstadoInvalidoError(
            f"Transición inválida: de {estado_actual.value} a {nuevo_estado.value}"
        )

def origenes_validos(nuevo_estado):
    origenes = []
    for estado, destinos in TRANSICIONES.items():
        if nuevo_estado in destinos:
            origenes.append(estado.value)
    return origenes

