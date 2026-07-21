from core_engine.models import EstadoLead, TRANSICIONES, Bitacora
from core_engine.exceptions import EstadoInvalidoError
from core_engine.repositories import LeadRepository, BitacoraRepository

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

class PipelineService:
    def __init__(self, conexion) -> None:
        self.conexion = conexion
        self.leads = LeadRepository(conexion)
        self.bitacora= BitacoraRepository(conexion)

    def avanzar_lead(self, lead_id, nuevo_estado, vendedor_id =None, notas= None):
        lead = self.leads.obtener_por_id(lead_id)
        if lead is None:
            raise ValueError(f"No existe el lead {lead_id}")

        estado_anterior = lead.estado_actual
        validar_transicion(estado_anterior, nuevo_estado)
        try:
            self.leads.actualizar_estado(lead_id, nuevo_estado)
            registro = Bitacora(lead_id, vendedor_id, estado_anterior.value, nuevo_estado.value, notas)
            self.bitacora.registrar_bitacora(registro)
            self.conexion.commit()
            return lead_id
        except Exception:
            self.conexion.rollback()
            raise



