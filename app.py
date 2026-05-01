import random
import time
import sqlite3
from datetime import datetime, timedelta
import schedule
import streamlit as st
import threading
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TRIPLE SAPOO", layout="wide")

# --- LÓGICA DE BASE DE DATOS ---
def inicializar_db():
    conexion = sqlite3.connect("sorteos_lotería.db", check_same_thread=False)
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
    conexion.close()

def ejecutar_sorteos_automaticos(hora_etiqueta):
    def generar_triple():
        return f"{random.randint(0, 999):03d}"

    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
              "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

    res_a = generar_triple()
    res_b = generar_triple()
    res_z = f"{random.randint(0, 999):03d} - {random.choice(signos)}"
    
    # El terminal son los últimos 2 dígitos del triple
    term_a = res_a[1:]
    term_b = res_b[1:]

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    conexion = sqlite3.connect("sorteos_lotería.db", check_same_thread=False)
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO resultados (fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fecha_hoy, hora_etiqueta, res_a, term_a, res_b, term_b, res_z))
    conexion.commit()
    conexion.close()

# --- HILO PARA EL RELOJ ---
def iniciar_reloj():
    schedule.every().day.at("13:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="01:00 PM")
    schedule.every().day.at("16:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="04:00 PM")
    schedule.every().day.at("21:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="09:00 PM")
    while True:
        schedule.run_pending()
        time.sleep(1)

if "reloj_iniciado" not in st.session_state:
    inicializar_db()
    threading.Thread(target=iniciar_reloj, daemon=True).start()
    st.session_state.reloj_iniciado = True

# --- INTERFAZ STREAMLIT ---
st.title("🐸 TRIPLE SAPOO")

# Contador Regresivo
def proximo_sorteo():
    ahora = datetime.now()
    horas = ["13:00", "16:00", "21:00"]
    futuros = [datetime.strptime(h, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in horas]
    pendientes = [h for h in futuros if h > ahora]
    
    if not pendientes:
        prox = futuros[0] + timedelta(days=1)
    else:
        prox = min(pendientes)
    
    dif = prox - ahora
    return str(dif).split(".")[0] # Formato HH:MM:SS

st.metric("Tiempo para el próximo sorteo", proximo_sorteo())

if st.button("🎲 Realizar Sorteo Manual"):
    ejecutar_sorteos_automaticos("MANUAL")
    st.rerun()

st.write("### Historial de Resultados")

# Mostrar Resultados
try:
    conn = sqlite3.connect("sorteos_lotería.db")
    df = pd.read_sql_query("SELECT fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal FROM resultados ORDER BY id DESC", conn)
    st.table(df)
    conn.close()
except:
    st.info("Esperando datos...")

# Refresco para el contador
time.sleep(1)
st.rerun()
