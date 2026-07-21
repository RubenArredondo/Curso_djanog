from enum import Enum
class EstadoLead(str, Enum):
    NUEVO = "Nuevo"
    CONTACTADO = "Contactado"
    NEGOCIACION = "Negociacion"
    GANADO = "Ganado"
    PERDIDO = "Perdido"

TRANSICIONES = {
    EstadoLead.NUEVO: [EstadoLead.CONTACTADO],
    EstadoLead.CONTACTADO: [EstadoLead.NEGOCIACION, EstadoLead.PERDIDO],
    EstadoLead.NEGOCIACION: [EstadoLead.GANADO, EstadoLead.PERDIDO],
    EstadoLead.GANADO: [],
    EstadoLead.PERDIDO: []
}
class Persona:
    def __init__(self, nombre, apellido, correo) -> None:
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo

    def get_fullname(self):
        ficha = f"{self.nombre} {self.apellido}".title()
        return ficha

class Lead(Persona):
    def __init__(self, nombre, apellido, correo, presupuesto_estimado) -> None:
        super().__init__(nombre, apellido, correo)
        self.id = None
        self.vendedor_id = None
        self.presupuesto = presupuesto_estimado
        self.estado_actual = EstadoLead.NUEVO
        self.prioridad = self.es_prioridad()
        self.corporativo = self.es_corporativo(correo)

    @property
    def presupuesto(self):
        return self._presupuesto
    @presupuesto.setter
    def presupuesto(self, valor):
        if valor < 0:
            raise ValueError ("El presupuesto no puede ser menor a 0")
        else:
            self._presupuesto = valor

    def es_prioridad(self):
        prioridad = ""
        if self.presupuesto >= 10000:
            prioridad = "Alta"
        elif self.presupuesto >= 5000:
            prioridad = "Media"
        else:
            prioridad = "Baja"
        return prioridad

    def es_corporativo(self, correo)  -> bool:
        dominios_comunes = ["yahoo", "gmail", "outlook", "icloud"]
        dominio = correo.split("@")[1].split(".")[0]
        return dominio not in dominios_comunes


    def __str__(self) -> str:
        return f"Nombre: {self.get_fullname()} Estado_actual: {self.estado_actual.value} Prioridad: {self.prioridad} Es corporativo: {self.corporativo}"


class Vendedor(Persona):
    def __init__(self, nombre, apellido,correo, n_empleado) -> None:
        super().__init__(nombre, apellido, correo)
        self.n_empleado = n_empleado

    def __str__(self) -> str:
        return f"Nombre: {self.get_fullname(), self.n_empleado}"

class Bitacora:
    def __init__(self, lead_id, vendedor_id, estado_anterior, estado_nuevo, notas) -> None:
        self.id = None
        self.lead_id = lead_id
        self.vendedor_id = vendedor_id
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo
        self.fecha_evento = None
        self.notas = notas

    def __str__(self) -> str:
        return f"""Bitacora Leads:
        ID Lead: {self.lead_id}
        ID Vendedor: {self.vendedor_id}
        Estado anterior: {self.estado_anterior}
        Nuevo Estado {self.estado_nuevo}
        Notas: {self.notas}
        """


