# 🐳 Guía Docker — Proyecto CRM Leads

Objetivo: correr el proyecto completo (PostgreSQL **y** la app Python) en
contenedores Docker, sin tocar el Postgres instalado en el Mac.

**Dos niveles de dockerización:**

| Nivel | Qué corre en Docker | Qué corre en el Mac |
|---|---|---|
| **1** | Solo PostgreSQL | La app, con el `.venv` |
| **2** | PostgreSQL + la app | Nada |

Esta guía cubre el **nivel 2**. El nivel 1 sigue sirviendo para desarrollar
rápido (editas código y corres sin reconstruir); está en la sección 4b.

---

## 1. Conceptos básicos

| Concepto | Qué es |
|---|---|
| **Imagen** | Plantilla congelada de un software (ej. `postgres:16` = PostgreSQL ya instalado). Se descargan de Docker Hub. |
| **Contenedor** | Una copia de esa imagen **corriendo**, aislada del Mac. Un "mini-ordenador" desechable. |
| **Puerto `-p 5433:5432`** | Cable entre tu Mac y el contenedor: lo que llega al puerto 5433 del Mac va al 5432 de dentro (donde escucha Postgres). Se usa 5433 para no chocar con el Postgres local del Mac (5432). |
| **Volumen `-v`** | "Pendrive" de datos que sobrevive aunque borres el contenedor. Sin volumen, borrar el contenedor = perder los datos. |
| **Docker Compose** | El comando `docker run` kilométrico convertido en un archivo (`docker-compose.yml`) dentro del proyecto: versionable en git y reproducible con un solo comando. |
| **Dockerfile** | La *receta* para construir una imagen propia (la de tu app). Docker la ejecuta línea por línea al hacer `docker compose build`. |
| **`requirements.txt`** | La lista del súper: qué librerías instalar dentro del contenedor. Sin él, el contenedor nace con Python pelón. |
| **`.dockerignore`** | Hermano del `.gitignore`: qué NO copiar al contenedor (`.venv`, `.git`, `.env`). |

### Flujo mental

```
Dockerfile  --(docker compose build)-->  Imagen  --(docker compose run)-->  Contenedor
  receta                                plantilla                            corriendo
```

Como en Python: el Dockerfile es el archivo con la clase, la imagen es la
clase, y el contenedor es el objeto instanciado.

### `RUN` vs `CMD` (la confusión clásica)

| | Cuándo se ejecuta | Cuántas veces |
|---|---|---|
| `RUN` | Al **construir** la imagen (`build`) | Una vez, queda horneado |
| `CMD` | Al **arrancar** el contenedor (`run`) | Cada vez |

> **Nota:** Docker Desktop (la app de la ballena) solo tiene que estar corriendo
> de fondo. La ventana/Dashboard no hace falta para nada: todo se hace por terminal.

---

## 2. Archivos

Los cuatro van en la raíz del proyecto, al lado de `main.py`.

### CREAR: `requirements.txt`

```
psycopg2-binary==2.9.12
python-dotenv==1.2.2
pytest==9.1.1
```

Se genera con `pip freeze > requirements.txt` (ojo con el `>`, sin él solo
imprime en pantalla). Conviene dejar solo lo que importas tú; pip resuelve
las dependencias de las dependencias.

### CREAR: `Dockerfile` (con D mayúscula, sin extensión)

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

| Instrucción | Qué hace |
|---|---|
| `FROM python:3.14-slim` | La base: Linux mínimo con Python ya instalado (`slim` ≈ 150MB en vez de 1GB) |
| `WORKDIR /app` | Crea y entra a `/app` **dentro** del contenedor |
| `COPY requirements.txt .` | Copia ese archivo del Mac al contenedor |
| `RUN pip install ...` | Instala las librerías durante la construcción |
| `COPY . .` | Copia el resto del proyecto |
| `CMD ["python", "main.py"]` | Comando por defecto al arrancar el contenedor |

**¿Por qué copiar `requirements.txt` aparte si después se copia todo?**
Por la **caché de capas**. Docker guarda cada instrucción como una capa
reutilizable. Si solo cambias `models.py`, Docker reutiliza la capa del
`pip install` y el build baja de ~2 minutos a ~2 segundos.

### CREAR: `.dockerignore`

```
.venv/
.git/
__pycache__/
.pytest_cache/
.DS_Store
.env
```

Sin esto, el `COPY . .` se llevaría el `.venv` entero (librerías compiladas
para macOS, inservibles dentro de Linux) y todo el historial de `.git`.

El `.env` se excluye **a propósito**: la configuración no se hornea en la
imagen, se inyecta al arrancar. Así la misma imagen sirve en cualquier
máquina cambiando solo variables.

### CREAR: `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16
    container_name: crm-postgres
    environment:
      POSTGRES_USER: toris
      POSTGRES_PASSWORD: crm2026
      POSTGRES_DB: crm_leads
    ports:
      - "5433:5432"
    volumes:
      - crm_datos:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U toris -d crm_leads"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: crm-app
    depends_on:
      db:
        condition: service_healthy
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_NAME: crm_leads
      DB_USER: toris
      DB_PASSWORD: crm2026
    stdin_open: true
    tty: true

volumes:
  crm_datos:
```

**La indentación (espacios) importa.** Cada bloque bajo `services:` es un
contenedor.

| Clave | Qué hace |
|---|---|
| `image:` vs `build:` | `db` descarga una imagen hecha; `app` **construye** desde tu Dockerfile (`.` = busca el Dockerfile aquí) |
| `environment:` | Variables inyectadas al contenedor. Las `POSTGRES_*` son especiales: la imagen oficial crea usuario y BD con ellas |
| `ports: "5433:5432"` | Izquierda = tu Mac, derecha = adentro. 5433 afuera para no chocar con el Postgres del Mac |
| `volumes:` | El "pendrive" que sobrevive al borrado del contenedor |
| `healthcheck:` | Postgres tarda segundos en aceptar conexiones; esto pregunta cada 5s si ya está listo |
| `depends_on: condition: service_healthy` | La app **espera** a que la BD esté sana. Sin esto: "connection refused" |
| `stdin_open` + `tty` | Conectan el teclado. Sin ellas el menú truena en el primer `input()` |

### 🔑 La línea más importante

```yaml
DB_HOST: db
```

No dice `localhost`, dice **`db`** — el nombre del servicio. Docker crea una
red privada donde cada servicio es alcanzable por su nombre, como un dominio.

Y `database.py` **no cambia ni una línea**: lee `os.getenv("DB_HOST")` y le da
igual si vale `localhost` o `db`. Por eso se separa configuración de código.

---

## 3. Puesta en marcha (primera vez)

Desde la carpeta `Proyecto Semana 1`:

```bash
# 1. Construir la imagen de la app (tarda 1-2 min la primera vez)
docker compose build

# 2. Levantar la base de datos en segundo plano
docker compose up -d db

# 3. Verificar (STATUS debe decir "Up ... (healthy)")
docker ps

# 4. El contenedor nace VACÍO: crear las tablas
docker compose run --rm app python -m core_engine.database

# 5. Correr el menú
docker compose run --rm app
```

> **Nota:** en el paso 4 el `python -m core_engine.database` **sobrescribe**
> el `CMD` del Dockerfile. Por eso `CMD` se llama "comando por defecto":
> se puede cambiar al vuelo.

### `run` vs `up`

| | Para qué |
|---|---|
| `up` | Servicios que corren solos (una BD, un servidor web) |
| `run` | Ejecutar algo **una vez**, con el teclado conectado — ideal para el menú interactivo |
| `--rm` | Borra ese contenedor al salir, para no acumular basura |

---

## 4. Flujo de trabajo día a día

```bash
docker compose up -d db          # al empezar
docker compose run --rm app      # trabajar
docker compose down              # al terminar (los datos quedan en el volumen)
```

### Cómo volver después de apagar

| Cómo lo apagaste | Qué hacer para volver |
|---|---|
| `docker compose down` | `docker compose up -d db` + `docker compose run --rm app` — **nada más**, los datos siguen |
| `docker compose down -v` | Lo mismo **+ recrear tablas**: `docker compose run --rm app python -m core_engine.database` |
| Cambiaste código Python | `docker compose build` **antes** de correr |

> ⚠️ **El error más común:** editas `models.py`, corres el contenedor y no
> pasa nada. La imagen tiene el código **horneado**: hay que hacer
> `docker compose build` después de cada cambio.

### 4b. Nivel 1 — solo la BD en Docker (desarrollo rápido)

Si estás editando código constantemente, reconstruir en cada cambio es lento.
Alternativa: deja solo Postgres en Docker y corre la app desde el Mac.

```bash
docker compose up -d db          # solo la base de datos
source .venv/bin/activate
python main.py                   # la app corre en el Mac
```

Requiere que el `.env` apunte al contenedor:

```
DB_HOST=localhost
DB_PORT=5433        # el puerto publicado por el contenedor
```

---

## 5. Chuleta de comandos

### Docker Compose (los del día a día)

| Comando | Qué hace |
|---|---|
| `docker compose build` | Construye la imagen de la app desde el `Dockerfile` |
| `docker compose up -d` | Lee el `.yml` y levanta todo (`-d` = en segundo plano) |
| `docker compose up -d db` | Levanta **solo** el servicio `db` |
| `docker compose run --rm app` | Corre la app una vez, con teclado; `--rm` la borra al salir |
| `docker compose run --rm app <comando>` | Ídem pero sobrescribiendo el `CMD` (ej. `python -m core_engine.database`) |
| `docker compose down` | Para y borra los contenedores — el **volumen sobrevive**, los datos siguen |
| `docker compose down -v` | Ídem + borra el volumen → **borrón total** (habrá que recrear tablas) |
| `docker compose ps` | Estado de los servicios del `.yml` |
| `docker compose logs db` | Logs del servicio `db` |
| `docker compose stop` / `start` | Apaga/prende **sin destruir** el contenedor (más rápido que down/up) |
| `docker compose -f otro.yml up -d` | Usar un archivo con otro nombre (`-f` = file). Útil con `docker-compose.dev.yml` / `.prod.yml` |

### Docker básico (contenedores sueltos)

| Comando | Qué hace |
|---|---|
| `docker ps` | Contenedores **corriendo** |
| `docker ps -a` | Todos, incluidos los parados |
| `docker stop crm-postgres` | Apaga el contenedor (datos intactos) |
| `docker start crm-postgres` | Lo vuelve a encender |
| `docker rm -f crm-postgres` | Lo destruye (con su disco interno, salvo lo que esté en volumen) |
| `docker logs crm-postgres` | Qué imprime por dentro (útil si no arranca) |
| `docker exec -it crm-postgres psql -U toris crm_leads` | Abre `psql` DENTRO del contenedor para mirar tablas a mano |
| `docker exec crm-postgres psql -U toris -d crm_leads -c "\dt"` | Lista las tablas sin entrar (`-c` = ejecuta y sal) |
| `docker images` | Imágenes (plantillas) descargadas |
| `docker volume ls` | Lista los volúmenes |

> `docker exec` = "ejecuta esto DENTRO de un contenedor que ya corre".
> `docker compose run` = "levanta un contenedor NUEVO para esto".

### Regla mental

> `down` normal = tus datos viven · `down -v` = empiezas de cero

---

## 6. Problemas que ya nos pasaron (y su solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `zsh: command not found: python` | El Mac no tiene `python` a secas y las librerías viven en el venv | `source .venv/bin/activate` y luego `python ...`, o llamar directo `.venv/bin/python ...` |
| "La app de Docker no abre" | La ventana no aparece, pero el motor SÍ corre de fondo (por eso los comandos funcionan) | Ignorarlo: la ventana no hace falta. Si se quiere: `Cmd+Tab` para buscarla, o `open -a Docker` |
| El `.dmg` desmontado | Era solo el instalador (la caja) | Nada que hacer: la app quedó en `/Applications` |
| Puerto ocupado al hacer `up` | El contenedor viejo de `docker run` sigue vivo | `docker rm -f crm-postgres` y repetir `docker compose up -d` |
| Cambié el código y el contenedor sigue igual | La imagen tiene el código horneado | `docker compose build` antes de correr |
| `pip freeze` imprime en pantalla y no crea el archivo | Faltó el `>` | `pip freeze > requirements.txt` |
| "No hay leads" tras dockerizar | Correcto: el Postgres del contenedor es **otro**, nace vacío. Los leads viejos están en el Postgres del Mac | Crear datos nuevos, o exportar/importar si se quieren migrar |
| `connection refused` al arrancar la app | La app arrancó antes que Postgres | Ya resuelto con `healthcheck` + `depends_on: service_healthy` |

---

## 7. Experimento para entender los volúmenes

1. Guarda un lead: `docker compose run --rm app` → opción 1.
2. `docker compose down` → `docker compose up -d db` → `docker compose run --rm app`
   → opción 3: ¿está el lead? **Sí** (el volumen sobrevive al `down`).
3. `docker compose down -v` → `docker compose up -d db` → ¿está? **No**, ni
   siquiera las tablas (el `-v` borró el volumen). Toca
   `docker compose run --rm app python -m core_engine.database` de nuevo.

---

## 8. Docker vs otras tecnologías (para no confundirse)

| Tecnología | Qué hace por debajo | Ejemplo |
|---|---|---|
| **Wine / CrossOver** | **Traduce llamadas**: el programa pide cosas de Windows y se traducen a Mac/Linux en vivo | Juegos de Windows en Mac |
| **Proton** | Lo mismo, es Wine mejorado por Valve | Steam Deck |
| **Rosetta 2** | **Emula CPU**: traduce instrucciones x86 a ARM | Apps Intel en Mac M-series |
| **Máquina virtual** | Emula una **computadora completa** con su propio sistema operativo | VirtualBox, VMware |
| **Docker** | **No emula nada**: aísla procesos que comparten el kernel de Linux | Este proyecto |

**Frase para el examen:** *una VM virtualiza hardware; un contenedor aísla
procesos compartiendo el kernel.*

Analogía: una VM es construir una **casa completa** en tu terreno (cimientos,
tuberías y luz propios). Un contenedor es un **departamento** en tu edificio:
paredes que te aíslan, pero compartes cimientos y servicios. Por eso caben 50
contenedores en una laptop y no 50 VMs.

> **Detalle de Mac:** como Docker necesita un kernel de Linux y macOS no lo
> tiene, Docker Desktop arranca una VM de Linux invisible y mete ahí los
> contenedores. En Linux nativo esa capa no existe.
