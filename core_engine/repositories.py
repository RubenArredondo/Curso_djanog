from core_engine.models import Lead, EstadoLead, Bitacora

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

    def actualizar_estado(self, lead_id, estado_nuevo):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE leads SET estado_actual =%s, fecha_actualizacion= NOW() WHERE id_lead= %s", (estado_nuevo.value, lead_id),)

class BitacoraRepository:
    def __init__(self, conexion) -> None:
        self.conexion = conexion

    def registrar_bitacora(self, bitacora: Bitacora):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO bitacora (estado_anterior, estado_nuevo, notas, lead_id, vendedor_id)
                VALUES (%s,%s,%s,%s,%s) RETURNING id""",
            (
                bitacora.estado_anterior,
                bitacora.estado_nuevo,
                bitacora.notas,
                bitacora.lead_id,
                bitacora.vendedor_id
            ),
        )
        return cursor.fetchone()[0]

    def listar_por_lead(self, lead_id):
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT id, lead_id, vendedor_id, estado_anterior, estado_nuevo, notas, fecha_evento
                FROM bitacora WHERE lead_id =%s
                ORDER BY fecha_evento
            """,
            (lead_id,),
        )
        filas = cursor.fetchall()
        registros = []

        for fila in filas:
            actualizacion = Bitacora(fila[1], fila[2], fila[3], fila[4], fila[5])
            actualizacion.id = fila[0]
            actualizacion.fecha_evento = fila[6]
            registros.append(actualizacion)
        return registros




