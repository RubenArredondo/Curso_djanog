from core_engine.database import obtener_conexion
from core_engine.models import Lead, EstadoLead
from core_engine.repositories import LeadRepository, BitacoraRepository
from core_engine.services import PipelineService
from core_engine.exceptions import EstadoInvalidoError


def mostrar_menu():
    print("\n===== CRM DE LEADS =====")
    print("1. Registrar nuevo lead")
    print("2. Mostrar Leads")
    print("3. Avanzar lead de estado")
    print("4. Buscar leads")
    print("5. Ver bitacora de un lead")
    print("6. Salir")


def registrar_lead(repo, conexion):
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    correo = input("Correo: ")
    presupuesto = float(input("Presupuesto estimado: "))

    lead = Lead(nombre, apellido, correo, presupuesto)
    nuevo_id = repo.guardar_lead(lead)
    conexion.commit()
    print(f"Lead registrado con id {nuevo_id}")


def avanzar_lead(servicio):
    lead_id = int(input("Id del lead: "))
    print("Estados disponibles:")
    for estado in EstadoLead:
        print(f"   - {estado.value}")
    texto = input("Nuevo estado: ")
    notas = input("Notas") or None

    try:
        nuevo_estado = EstadoLead(texto)
    except ValueError:
        print("Ese estado no existe")
        return

    try:
        servicio.avanzar_lead(lead_id, nuevo_estado, notas=notas)
        print("Estado actualizado correctamente")
    except EstadoInvalidoError as error:
        print(f"No se pudo avanzar: {error}")
    except ValueError as error:
        print(error)

def imprimir_leads(resultados):
    if not resultados:
        print("No se encontraron leads")
        return
    for lead in resultados:
        print(f"   id={lead.id} | {lead.get_fullname()} | {lead.estado_actual.value} | {lead.prioridad}")


def mostrar_leads(repo):
    resultados = repo.buscar_leads()
    imprimir_leads(resultados)

def buscar_leads(repo):
    estado = input("Filtrar por estado enter para omitir: ") or None
    prioridad = input("Filtrar por prioridad enter para omitir ") or None

    resultados = repo.buscar_leads(estado=estado, prioridad=prioridad)
    imprimir_leads(resultados)


def ver_bitacora(repo_bitacora):
    lead_id = int(input("Id del lead: "))
    registros = repo_bitacora.listar_por_lead(lead_id)
    if not registros:
        print("Ese lead no tiene movimientos")
        return
    for registro in registros:
        print(f"   {registro.fecha_evento} | {registro.estado_anterior} -> {registro.estado_nuevo} | {registro.notas}")


def main():
    conexion = obtener_conexion()
    repo_leads = LeadRepository(conexion)
    repo_bitacora = BitacoraRepository(conexion)
    servicio = PipelineService(conexion)

    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ")

        if opcion == "1":
            registrar_lead(repo_leads, conexion)
        elif opcion == "2":
            mostrar_leads(repo_leads)
        elif opcion == "3":
            avanzar_lead(servicio)
        elif opcion == "4":
            buscar_leads(repo_leads)
        elif opcion == "5":
            ver_bitacora(repo_bitacora)
        elif opcion == "6":
            print("Cerrando Programa")
            break
        else:
            print("Opcion no valida")

    conexion.close()


if __name__ == "__main__":
    main()
