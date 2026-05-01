import streamlit as st
import random
import time
import sqlite3
import pandas as pd
import threading
from datetime import datetime, timedelta
import schedule

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TRIPLE SAPOO", layout="wide")

# Título con formato estándar para evitar errores de renderizado
st.title("🐸 TRIPLE SAPOO - Resultados")
st.write("---")

# --- 2. LÓGICA DE BASE DE DATOS ---
def inicializar_db():
    try:
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
    except Exception as e:
        pass

def ejecutar_sorteo(hora_etiqueta):
    t_a = f"{random.randint(0, 999):03d}"
    t_b = f"{random.randint(0, 999):03d}"
    signos = ["ARIES", "TAURO", "GÉMINIS", "CÁNCER", "LEO", "VIRGO", 
              "LIBRA", "ESCORPIO", "SAGITARIO", "CAPRICORNIO", "ACUARIO", "PISCIS"]
    num_z = f"{random.randint(0, 999):03d}"
    res_zodiacal = f"{num_z} - {random.choice(signos)}"
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    try:
        with sqlite3.connect("sorteos_lotería.db", check_same_thread=False) as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO resultados (fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_hoy, hora_etiqueta, t_a, t_a[1:], t_b, t_b[1:], res_zodiacal))
            conexion.commit()
    except Exception as e:
        print(f"Error en sorteo: {e}")

# --- 3. FUNCIONES DEL CONTADOR ---
def obtener_proximo_sorteo():
    ahora = datetime.now()
    # Horarios definidos: 1:00 PM (13h), 4:00 PM (16h), 9:00 PM (21h)
    programados = ["13:00", "16:00", "21:00"]
    futuros = []
    
    for h in programados:
        h_obj = datetime.strptime(h, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        if h_obj > ahora:
            futuros.append(h_obj)
    
    if not futuros:
        proximo = datetime.strptime("13:00", "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) + timedelta(days=1)
    else:
        proximo = min(futuros)
        
    restante = proximo - ahora
    return proximo.strftime("%I:%M %p"), restante

# --- 4. CONTROL DE HILO SECUNDARIO ---
if "hilo_activo" not in st.session_state:
    inicializar_db()
    
    def worker():
        schedule.every().day.at("13:00").do(ejecutar_sorteo, hora_etiqueta="01:00 PM")
        schedule.every().day.at("16:00").do(ejecutar_sorteo, hora_etiqueta="04:00 PM")
        schedule.every().day.at("21:00").do(ejecutar_sorteo, hora_etiqueta="09:00 PM")
        while True:
            schedule.run_pending()
            time.sleep(1)

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    st.session_state.hilo_activo = True

# --- 5. INTERFAZ DE USUARIO ---
prox_hora, t_faltante = obtener_proximo_sorteo()

# Encabezado del contador
st.subheader(f"Próximo Sorteo Programado: {prox_hora}")
segundos_totales = int(t_faltante.total_seconds())
hh, mm = divmod(segundos_totales // 60, 60)
ss = segundos_totales % 60
st.metric(label="Cuenta Regresiva", value=f"{hh:02d}:{mm:02d}:{ss:02d}")

# Botones
c1, c2 = st.columns(2)
with c1:
    if st.button("🎲 Realizar Sorteo Manual"):
        ejecutar_sorteo("MANUAL")
        st.rerun()
with c2:
    if st.button("🔄 Refrescar"):
        st.rerun()

st.write("### 📋 Historial de Resultados")

# Mostrar Tabla
try:
    with sqlite3.connect("sorteos_lotería.db") as conn:
        df = pd.read_sql_query("SELECT fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal FROM resultados ORDER BY id DESC", conn)
    
    if not df.empty:
        df.columns = ["Fecha", "Sorteo", "Triple A", "Term. A", "Triple B", "Term. B", "Zodiacal"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay resultados registrados.")
except Exception:
    st.error("Iniciando sistema de datos...")

# Auto-recarga cada 10 segundos para actualizar el contador
time.sleep(10)
st.rerun()
