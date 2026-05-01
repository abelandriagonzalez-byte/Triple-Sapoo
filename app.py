import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import threading
from datetime import datetime
import schedule

# --- 1. CONFIGURACIÓN DE LA BASE DE DATOS ---
def inicializar_db():
    with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                hora_programada TEXT,
                triple_a TEXT,
                terminal_a TEXT,
                triple_b TEXT,
                terminal_b TEXT,
                zodiacal TEXT
            )
        ''')
        conexion.commit()

# --- 2. LÓGICA DEL SORTEO ---
def ejecutar_sorteo(hora_etiqueta):
    # Generar números aleatorios de 3 dígitos
    num_a = random.randint(0, 999)
    num_b = random.randint(0, 999)
    num_z = random.randint(0, 999)
    
    t_a = f"{num_a:03d}"
    t_b = f"{num_b:03d}"
    term_a = t_a[1:] # Últimos 2 dígitos
    term_b = t_b[1:]
    
    signos = ["ARIES", "TAURO", "GÉMINIS", "CÁNCER", "LEO", "VIRGO", 
              "LIBRA", "ESCORPIO", "SAGITARIO", "CAPRICORNIO", "ACUARIO", "PISCIS"]
    res_zodiacal = f"{num_z:03d} - {random.choice(signos)}"
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    try:
        with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO resultados (fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_hoy, hora_etiqueta, t_a, term_a, t_b, term_b, res_zodiacal))
            conexion.commit()
        print(f"Sorteo Guardado: {hora_etiqueta}")
    except Exception as e:
        print(f"Error al guardar sorteo: {e}")

# --- 3. HILO DE FONDO PARA PROGRAMACIÓN (SCHEDULE) ---
def run_schedule():
    # Programar las horas exactas
    schedule.every().day.at("13:00").do(ejecutar_sorteo, hora_etiqueta="01:00 PM")
    schedule.every().day.at("16:00").do(ejecutar_sorteo, hora_etiqueta="04:00 PM")
    schedule.every().day.at("21:00").do(ejecutar_sorteo, hora_etiqueta="09:00 PM")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar el hilo solo una vez al arrancar la app
if "hilo_activo" not in st.session_state:
    inicializar_db()
    t = threading.Thread(target=run_schedule, daemon=True)
    t.start()
    st.session_state.hilo_activo = True

# --- 4. INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Sistema de Sorteos", layout="wide")

st.title("🎰 Resultados de Lotería")
st.markdown("Los sorteos se realizan automáticamente a la **1:00 PM, 4:00 PM y 9:00 PM**.")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
with col2:
    if st.button("🎲 Simular Sorteo Manual"):
        ejecutar_sorteo("MANUAL")
        st.success("¡Sorteo generado!")
        st.rerun()

# Mostrar los datos
try:
    with sqlite3.connect("sorteos_lotería.db") as conn:
        # Traer todos los datos ordenados por los más recientes primero
        df = pd.read_sql_query("SELECT fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal FROM resultados ORDER BY id DESC", conn)
    
    if not df.empty:
        # Renombrar columnas para la vista del usuario
        df.columns = ["Fecha", "Hora", "Triple A", "Term. A", "Triple B", "Term. B", "Signo Zodiacal"]
        st.table(df)
    else:
        st.info("No hay resultados registrados hoy.")
except Exception as e:
    st.error(f"Error al cargar la tabla: {e}")
