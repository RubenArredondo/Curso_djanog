import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def obtener_conexion():
    conexion = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        dbname=os.getenv("DB_NAME"),
        password=os.getenv("DB_PASSWORD"),
    )
    return conexion

RUTA_DB = Path(__file__).resolve().parent.parent / "Partida_guardada.db"

def inicializar_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gremios(
            id SERIAL PRIMARY KEY,
            nombre_gremio TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personajes(
            id SERIAL PRIMARY KEY,
            nombre TEXT UNIQUE NOT NULL,
            salud_maxima INTEGER NOT NULL,
            tipo_clase TEXT NOT NULL,
            puntos_armadura INTEGER DEFAULT 0,
            mana_maximo INTEGER DEFAULT 0,
            multiplicador_dano REAL DEFAULT 1.0,
            gremio_id INTEGER,
            FOREIGN KEY (gremio_id) REFERENCES gremios(id)
        )
    """)

    conexion.commit()
    conexion.close()
