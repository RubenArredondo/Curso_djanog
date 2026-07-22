import pytest
from core_engine.database import obtener_conexion
from core_engine.models import Lead
from core_engine.repositories import LeadRepository


@pytest.fixture
def conexion():
    conn = obtener_conexion()
    yield conn
    conn.close()


@pytest.fixture
def lead_de_prueba(conexion):
    repo = LeadRepository(conexion)
    lead_id = repo.guardar_lead(Lead("Pancho", "Pantera", "panchito@gmail.com", 5000))
    conexion.commit()

    yield lead_id

    cursor = conexion.cursor()
    cursor.execute("DELETE FROM bitacora WHERE lead_id = %s", (lead_id,))
    cursor.execute("DELETE FROM leads WHERE id_lead = %s", (lead_id,))
    conexion.commit()
