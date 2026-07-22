import pytest
from core_engine.models import EstadoLead
from core_engine.services import validar_transicion, PipelineService
from core_engine.exceptions import EstadoInvalidoError
from core_engine.repositories import LeadRepository

@pytest.mark.parametrize("estado_actual, nuevo_estado", [
    (EstadoLead.NUEVO, EstadoLead.NEGOCIACION),
    (EstadoLead.NUEVO, EstadoLead.GANADO),
    (EstadoLead.NUEVO, EstadoLead.PERDIDO),
    (EstadoLead.CONTACTADO, EstadoLead.GANADO),
    (EstadoLead.CONTACTADO, EstadoLead.NUEVO),
    (EstadoLead.NEGOCIACION, EstadoLead.CONTACTADO),
    (EstadoLead.NEGOCIACION, EstadoLead.NUEVO),
    (EstadoLead.GANADO, EstadoLead.NUEVO),
    (EstadoLead.GANADO, EstadoLead.CONTACTADO),
    (EstadoLead.GANADO, EstadoLead.NEGOCIACION),
    (EstadoLead.GANADO, EstadoLead.PERDIDO),
    (EstadoLead.PERDIDO, EstadoLead.NUEVO),
    (EstadoLead.PERDIDO, EstadoLead.CONTACTADO),
    (EstadoLead.PERDIDO, EstadoLead.NEGOCIACION),
    (EstadoLead.PERDIDO, EstadoLead.GANADO),
])
def test_transiciones(estado_actual, nuevo_estado):
    with pytest.raises(EstadoInvalidoError):
        validar_transicion(estado_actual, nuevo_estado)

def test_transicion_valida_crea_bitacora(conexion, lead_de_prueba):
    servicio = PipelineService(conexion)
    servicio.avanzar_lead(lead_de_prueba, EstadoLead.CONTACTADO, None, "Primer contacto")

    cursor = conexion.cursor()
    cursor.execute(
        "SELECT estado_actual FROM leads WHERE id_lead = %s", (lead_de_prueba,)
    )
    assert cursor.fetchone()[0] == EstadoLead.CONTACTADO.value

    cursor.execute(
        "SELECT estado_anterior, estado_nuevo FROM bitacora WHERE lead_id = %s",
        (lead_de_prueba,),
    )
    filas = cursor.fetchall()
    assert len(filas) == 1
    assert filas[0] == (EstadoLead.NUEVO.value, EstadoLead.CONTACTADO.value)

# Extra: el buscador dinamico filtra sin romperse cuando hay parametros en None
def test_buscar_leads_filtra_por_estado(conexion, lead_de_prueba):
    repo = LeadRepository(conexion)
    resultados = repo.buscar_leads(estado=EstadoLead.NUEVO)
    ids = [lead.id for lead in resultados]
    assert lead_de_prueba in ids
