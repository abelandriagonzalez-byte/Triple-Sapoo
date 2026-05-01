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
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🐸 TRIPLE SAPOO 🎰</h1>", unsafe_allow_key=True)

# --- 2. LÓGICA DE BASE DE DATOS ---
def inicializar_db():
    with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT, hora_programada TEXT,
                triple_a TEXT, terminal_a TEXT,
                triple_b TEXT, terminal_b TEXT, zodiacal TEXT
            )
        ''')
        conexion.commit()

def ejecutar_sorteo(hora_etiqueta):
    t_a = f"{random.randint(0, 999):03d}"
    t_b = f"{random.randint(0, 999):03d}"
    signos = ["ARIES", "TAURO", "GÉMINIS", "CÁNCER", "LEO", "VIRGO", "LIBRA", "ESCORPIO", "SAGITARIO", "CAPRICORNIO", "ACUARIO", "PISCIS"]
    res_zodiacal = f"{random.randint(0, 999):03d} - {random.choice(signos)}"
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
        cursor = conexion.cursor()
        cursor.execute('INSERT INTO resultados (fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (fecha_hoy, hora_etiqueta, t_a, t_a[1:], t_b, t_b[1:], res_zodiacal))
        conexion.commit()

# --- 3. CONTADOR REGRESIVO ---
def obtener_proximo_sorteo():
    ahora = datetime.now()
    horarios = ["13:00", "16:00", "21:00"]
    futuros = []
    for h in horarios:
        obj_h = datetime.strptime(h, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        if obj_h > ahora:
            futuros.append(obj_h)
    
    if not futuros: # Si ya pasaron todos, el próximo es mañana a la 1 PM
        futuros.append(datetime.strptime("13:00", "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) + timedelta(days=1))
    
    proximo = min(futuros)
    restante = proximo - ahora
    return proximo.strftime("%I:%00 %p"), restante

# --- 4. HILO SECUNDARIO ---
def run_schedule():
    schedule.every().day.at("13:00").do(ejecutar_sorteo, hora_etiqueta="01:00 PM")
    schedule.every().day.at("16:00").do(ejecutar_sorteo, hora_etiqueta="04:00 PM")
    schedule.every().day.at("21:00").do(ejecutar_sorteo, hora_etiqueta="09:00 PM")
    while True:
        schedule.run_pending()
        time.sleep(1)

if "hilo_activo" not in st.session_state:
    inicializar_db()
    threading.Thread(target=run_schedule, daemon=True).start()
    st.session_state.hilo_activo = True

# --- 5. INTERFAZ VISUAL ---
# Sección del Contador
prox_nombre, tiempo_faltante = obtener_proximo_sorteo()
st.subheader(f"Próximo Sorteo: {prox_nombre}")
m, s = divmod(int(tiempo_faltante.total_seconds()), 60)
h, m = divmod(m, 60)
st.metric(label="Tiempo Restante", value=f"{h:02d}:{m:02d}:{s:02d}")

# Botones de Acción
col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 Sorteo Manual (Prueba)"):
        ejecutar_sorteo("MANUAL")
        st.rerun()
with col2:
    if st.button("🔄 Actualizar"):
        st.rerun()

# Tabla de Resultados
st.write("---")
st.markdown("### 📋 Historial de Resultados")
try:
    with sqlite3.connect("sorteos_lotería.db") as conn:
        df = pd.read_sql_query("SELECT fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal FROM resultados ORDER BY id DESC", conn)
    
    if not df.empty:
        df.columns = ["Fecha", "Sorteo", "Triple A", "Term. A", "Triple B", "Term. B", "Zodiacal"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin sorteos realizados hoy.")
except:
    st.error("Error al cargar la base de datos.")

# Autorefresco cada 30 segundos para actualizar el contador
time.sleep(30)
st.rerun()
