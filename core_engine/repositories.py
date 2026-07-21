from core_engine.models import Lead, EstadoLead

class LeadRepository:
    def __init__(self, conexion) -> None:
        self.conexion = conexion

    def guardar_lead(self, lead: Lead):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO leads (nombre, apellido, correo, presupuesto, estado_actual, es_corporativo, prioridad)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id_lead""",
            (
                lead.nombre,
                lead.apellido,
                lead.correo,
                lead.presupuesto,
                lead.estado_actual.value,
                lead.corporativo,
                lead.prioridad
            ),
        )
        resultado = cursor.fetchone()
        if resultado is None:
            raise RuntimeError("No se pudo obtener el id del lead insertado")
        nuevo_id = resultado[0]
        return nuevo_id

    def obtener_por_id(self, lead_id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT nombre, apellido, correo, presupuesto, estado_actual FROM leads WHERE id_lead = %s ",
            (lead_id,),)
        fila = cursor.fetchone()
        if fila is None:
            return None
        lead = Lead(fila[0], fila[1], fila[2], fila[3])
        lead.id  = lead_id
        lead.estado_actual = EstadoLead(fila[4])
        return lead

