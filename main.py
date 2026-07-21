from core_engine.database import obtener_conexion
from core_engine.models import Lead
from core_engine.repositories import LeadRepository

conexion = obtener_conexion()
repo = LeadRepository(conexion)
lead = Lead("Carlos", "Ruiz", "carlos@acme.com", 8000)
nuevo_id = repo.guardar_lead(lead)
conexion.commit()          # ← TÚ haces el commit, como hará el servicio
conexion.close()
print(f"Lead guardado con id {nuevo_id}")

