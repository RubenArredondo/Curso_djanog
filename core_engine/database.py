import os
import psycopg2
from dotenv import load_dotenv

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

def inicializar_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores(
        id_vendedor SERIAL PRIMARY KEY,
        n_empleado TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads(
        id_lead SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        correo TEXT NOT NULL,
        presupuesto NUMERIC NOT NULL,
        estado_actual TEXT DEFAULT 'Nuevo',
        es_corporativo BOOLEAN NOT NULL,
        prioridad TEXT NOT NULL,
        fecha_actualizacion TIMESTAMP DEFAULT NOW(),
        vendedor_id INTEGER REFERENCES vendedores(id_vendedor)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora(
            id SERIAL PRIMARY KEY,
            estado_anterior TEXT,
            estado_nuevo TEXT NOT NULL,
            notas TEXT ,
            fecha_evento TIMESTAMP DEFAULT NOW(),
            lead_id INTEGER REFERENCES leads(id_lead),
            vendedor_id INTEGER REFERENCES vendedores(id_vendedor)
        )
    """)

    conexion.commit()
    conexion.close()
    
    print("Base datos inicializad")
if __name__ == "__main__":
    inicializar_db()

