

from core_engine.models import EstadoLead, TRANSICIONES
from core_engine.exceptions import EstadoInvalidoError

def validar_transicion(estado_actual, nuevo_estado):
    destinos = TRANSICIONES[estado_actual]
    if nuevo_estado not in destinos:
        raise EstadoInvalidoError(
            f"Transición inválida: de {estado_actual.value} a {nuevo_estado.value}"

if __name__ == "__main__":
    validar_transicion()
