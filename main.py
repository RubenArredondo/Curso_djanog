from core_engine.database import obtener_conexion
from core_engine.models import Lead, Vendedor, EstadoLead
from core_engine.repositories import LeadRepository, BitacoraRepository, VendedorRepository
from core_engine.services import PipelineService
from core_engine.exceptions import EstadoInvalidoError


def mostrar_menu():
    print("\n===== CRM DE LEADS =====")
    print("1. Registrar nuevo lead")
    print("2. Registrar nuevo vendedor")
    print("3. Mostrar Leads")
    print("4. Mostrar Vendedores")
    print("5. Avanzar lead de estado")
    print("6. Asignar vendedor")
    print("7. Buscar leads")
    print("8. Ver bitacora")
    print("9. Buscar vendedor")
    print("10. Salir")


def registrar_lead(repo_lead, conexion):
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    correo = input("Correo: ")
    presupuesto = float(input("Presupuesto estimado: "))

    lead = Lead(nombre, apellido, correo, presupuesto)
    nuevo_id = repo_lead.guardar_lead(lead)
    conexion.commit()
    print(f"Lead registrado con id {nuevo_id}")


def avanzar_lead(servicio):
    lead_id = int(input("Id del lead: "))
    print("Estados disponibles:")
    for estado in EstadoLead:
        print(f"{estado.value}")
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


def mostrar_leads(repo_lead):
    resultados = repo_lead.buscar_leads()
    imprimir_leads(resultados)

def buscar_leads(repo_lead):
    estado = input("Filtrar por estado enter para omitir: ") or None
    prioridad = input("Filtrar por prioridad enter para omitir ") or None
    vendedor_id = input("Filtrar por id del vendedor enter para omitir ") or None
    if vendedor_id is not None:
        vendedor_id = int(vendedor_id)
    resultados = repo_lead.buscar_leads(estado=estado, prioridad=prioridad, vendedor_id= vendedor_id)
    imprimir_leads(resultados)

def registrar_vendedor(repo_vendedor, conexion):
    nombre = input("Ingrese el nombre: ")
    n_empleado = input("Ingrese el numero de vendedor (Ejemplo V-78): ")
    vendedor = Vendedor(n_empleado, nombre)
    nuevo_id = repo_vendedor.guardar_vendedor(vendedor)
    conexion.commit()
    print(f"Vendedor registrado con id {nuevo_id}")

def imprimir_vendedor(resultados):
    if not resultados:
        print("No se encontraron vendedores")
        return
    for vendedor in resultados:
        print(f"   id={vendedor.id} | {vendedor.nombre} | {vendedor.n_empleado}")


def buscar_vendedor(repo_vendedor):
    id_vendedor = int(input("Ingrese el id del vendedor:"))
    vendedor = repo_vendedor.obtener_por_id(id_vendedor)
    if vendedor is None:
        print("No existe vendedor")
        return
    imprimir_vendedor([vendedor])

def mostrar_vendedores(repo_vendedor):
    resultados = repo_vendedor.listar_todos()
    if resultados == []:
        print(f"No hay vendedores registrados")
        return
    imprimir_vendedor(resultados)

def asignar_vendedor(servicio):
    id_lead = int(input("ID del Lead: "))
    id_vendedor = int(input("ID del Vendedor: "))
    notas = input("Tiene alguna nota?(Opciona): ") or None
    try:
        servicio.asignar_vendedor(id_lead,id_vendedor,notas)
        print("Vendedor asignado correctamente")
    except ValueError as e:
        print(e)

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
    repo_vendedor = VendedorRepository(conexion)
    servicio = PipelineService(conexion)


    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ")

        if opcion == "1":
            registrar_lead(repo_leads, conexion)
        elif opcion == "2":
            registrar_vendedor(repo_vendedor, conexion)
        elif opcion == "3":
            mostrar_leads(repo_leads)
        elif opcion == "4":
            mostrar_vendedores(repo_vendedor)
        elif opcion == "5":
            avanzar_lead(servicio)
        elif opcion == "6":
            asignar_vendedor(servicio)
        elif opcion == "7":
            buscar_leads(repo_leads)
        elif opcion == "8":
            ver_bitacora(repo_bitacora)
        elif opcion == "9":
            buscar_vendedor(repo_vendedor)
        elif opcion == "10":
            print("Cerrando Programa")
            break
        else:
            print("Opcion no valida")

    conexion.close()


if __name__ == "__main__":
    main()
