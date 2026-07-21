# 🐳 Guía Docker — Proyecto CRM Leads

Objetivo: correr el PostgreSQL del proyecto en un contenedor Docker,
sin tocar el Postgres instalado en el Mac.

---

## 1. Conceptos básicos

| Concepto | Qué es |
|---|---|
| **Imagen** | Plantilla congelada de un software (ej. `postgres:16` = PostgreSQL ya instalado). Se descargan de Docker Hub. |
| **Contenedor** | Una copia de esa imagen **corriendo**, aislada del Mac. Un "mini-ordenador" desechable. |
| **Puerto `-p 5433:5432`** | Cable entre tu Mac y el contenedor: lo que llega al puerto 5433 del Mac va al 5432 de dentro (donde escucha Postgres). Se usa 5433 para no chocar con el Postgres local del Mac (5432). |
| **Volumen `-v`** | "Pendrive" de datos que sobrevive aunque borres el contenedor. Sin volumen, borrar el contenedor = perder los datos. |
| **Docker Compose** | El comando `docker run` kilométrico convertido en un archivo (`docker-compose.yml`) dentro del proyecto: versionable en git y reproducible con un solo comando. |

> **Nota:** Docker Desktop (la app de la ballena) solo tiene que estar corriendo
> de fondo. La ventana/Dashboard no hace falta para nada: todo se hace por terminal.

---

## 2. Archivos

### CREAR: `docker-compose.yml` (en la raíz del proyecto, al lado de `main.py`)

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

volumes:
  crm_datos:
```

Cada línea equivale a un flag del `docker run`: `environment` = los `-e`,
`ports` = el `-p`, `volumes` = el `-v`. **La indentación (espacios) importa.**

### MODIFICAR: `.env` (una sola línea)

```
DB_PORT=5433        # antes era 5432
```

El código Python no se toca: él solo lee el `.env` y se conecta al puerto.

---

## 3. Puesta en marcha (primera vez)

Desde la carpeta `Proyecto Semana 1`:

```bash
# 1. Si existe el contenedor viejo (creado con docker run), bórralo
#    para liberar el nombre y el puerto:
docker rm -f crm-postgres

# 2. Levantar todo desde el docker-compose.yml:
docker compose up -d

# 3. Verificar que corre (STATUS debe decir "Up ..."):
docker ps

# 4. El contenedor nace VACÍO: crear las tablas con el script del proyecto:
.venv/bin/python -m core_engine.database

# 5. Prueba de fuego — los 17 tests en verde:
.venv/bin/pytest tests/ -v
```

---

## 4. Flujo de trabajo día a día

```bash
docker compose up -d          # al empezar a trabajar
source .venv/bin/activate     # activar el venv (aparece (.venv) en el prompt)
pytest tests/ -v              # trabajar normal
docker compose down           # al terminar (los datos quedan en el volumen)
```

---

## 5. Chuleta de comandos

### Docker Compose (los del día a día)

| Comando | Qué hace |
|---|---|
| `docker compose up -d` | Lee el `.yml` y levanta todo (`-d` = en segundo plano) |
| `docker compose down` | Para y borra el contenedor — el **volumen sobrevive**, los datos siguen |
| `docker compose down -v` | Ídem + borra el volumen → **borrón total** (habrá que recrear tablas) |
| `docker compose ps` | Estado de los servicios del `.yml` |
| `docker compose logs db` | Logs del servicio `db` |

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
| `docker images` | Imágenes (plantillas) descargadas |
| `docker volume ls` | Lista los volúmenes |

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

---

## 7. Experimento para entender los volúmenes

1. Guarda un lead con `main.py`.
2. `docker compose down` → `docker compose up -d` → ¿está el lead? **Sí** (el volumen sobrevive al `down`).
3. `docker compose down -v` → `docker compose up -d` → ¿está? **No**, ni siquiera las tablas (el `-v` borró el volumen). Toca `python -m core_engine.database` de nuevo.
