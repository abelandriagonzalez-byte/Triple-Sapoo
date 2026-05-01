import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import threading
from datetime import datetime, timedelta
import schedule

# --- 1. CONFIGURACIÓN DE PÁGINA Y TÍTULO ---
st.set_page_config(page_title="TRIPLE SAPOO", layout="wide")
st.title("🐸 TRIPLE SAPOO")

# --- 2. LÓGICA DE LA BASE DE DATOS ---
def inicializar_db():
    with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
        cursor = conexion.cursor()
        # Estructura original: fecha, hora, sorteos A, B, C y Zodiacal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                hora_programada TEXT,
                sorteo_a TEXT,
                sorteo_b TEXT,
                sorteo_c TEXT,
                zodiacal TEXT
            )
        ''')
        conexion.commit()

def ejecutar_sorteos_automaticos(hora_etiqueta):
    def generar_triple():
        return "".join([str(random.randint(0, 9)) for _ in range(3)])

    signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", 
              "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

    res_a = generar_triple()
    res_b = generar_triple()
    res_c = generar_triple()
    res_z = random.choice(signos)

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO resultados (fecha, hora_programada, sorteo_a, sorteo_b, sorteo_c, zodiacal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha_hoy, hora_etiqueta, res_a, res_b, res_c, res_z))
        conexion.commit()

# --- 3. PROCESO EN SEGUNDO PLANO (RELOJ) ---
def run_schedule():
    # Programación de horarios originales
    schedule.every().day.at("13:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="01:00 PM")
    schedule.every().day.at("16:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="04:00 PM")
    schedule.every().day.at("21:00").do(ejecutar_sorteos_automaticos, hora_etiqueta="09:00 PM")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar el hilo del sorteador una sola vez
if "hilo_iniciado" not in st.session_state:
    inicializar_db()
    t = threading.Thread(target=run_schedule, daemon=True)
    t.start()
    st.session_state.hilo_iniciado = True

# --- 4. CONTADOR REGRESIVO ---
def obtener_tiempo_restante():
    ahora = datetime.now()
    horarios = ["13:00", "16:00", "21:00"]
    proximos = []
    for h in horarios:
        h_obj = datetime.strptime(h, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        if h_obj > ahora:
            proximos.append(h_obj)
    
    if not proximos:
        # Si pasaron todos los sorteos, el próximo es mañana a la 1:00 PM
        prox = datetime.strptime("13:00", "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) + timedelta(days=1)
    else:
        prox = min(proximos)
    
    faltante = prox - ahora
    segundos = int(faltante.total_seconds())
    hh, mm = divmod(segundos // 60, 60)
    ss = segundos % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}", prox.strftime("%I:%00 %p")

# --- 5. INTERFAZ VISUAL ---
tiempo_str, prox_hora_str = obtener_tiempo_restante()

st.subheader(f"Próximo Sorteo: {prox_hora_str}")
st.metric("Cuenta Regresiva", tiempo_str)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 Sorteo Manual"):
        ejecutar_sorteos_automaticos("MANUAL")
        st.rerun()
with col2:
    if st.button("🔄 Actualizar"):
        st.rerun()

st.write("### 📋 Historial de Resultados")

try:
    with sqlite3.connect("sorteos_lotería.db") as conn:
        df = pd.read_sql_query("SELECT fecha, hora_programada, sorteo_a, sorteo_b, sorteo_c, zodiacal FROM resultados ORDER BY id DESC", conn)
    
    if not df.empty:
        df.columns = ["Fecha", "Hora", "Sorteo A", "Sorteo B", "Sorteo C", "Signo"]
        st.table(df)
    else:
        st.info("Esperando los sorteos programados...")
except:
    st.error("Iniciando base de datos...")

# Auto-refresco cada 10 segundos para actualizar el contador
time.sleep(10)
st.rerun()
