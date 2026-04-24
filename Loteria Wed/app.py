import streamlit as st
import sqlite3
import random
import time
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Lotería de Mara", layout="wide")

# Estilo personalizado (Verde Triple Sapo)
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; }
    .card { background-color: #2d5a27; border: 3px solid #ccff00; padding: 20px; border-radius: 15px; text-align: center; }
    .timer { font-size: 80px !important; font-family: 'Courier New'; color: #ccff00; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, 
                    a TEXT, b TEXT, c TEXT, signo TEXT)''')
    return conn

conn = conectar_db()

def obtener_resultado(hora):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha_hoy, hora))
    return cursor.fetchone()

# --- INTERFAZ ---
# Encabezado
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("<h1 style='text-align: center; color: #ccff00;'>TRIPLE SAPO</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ffff00;'>DE SU LOTERÍA DE MARA</h3>", unsafe_allow_html=True)

# Reloj y Contador
ahora = datetime.now()
st.sidebar.metric("Hora Actual", ahora.strftime("%I:%M:%S %p"))

horarios = ["13:05:00", "17:05:00", "21:05:00"]
futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in horarios]
futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
proximo = min(futuros)
restante = proximo - ahora

st.markdown(f"<div class='timer'>{str(restante).split('.')[0]}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>PRÓXIMO SORTEO EN</p>", unsafe_allow_html=True)

# Tablero de Resultados
st.write("---")
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]
cols = st.columns(3)

for i, hora in enumerate(h_labels):
    with cols[i]:
        res = obtener_resultado(hora)
        color = ["#ffcc00", "#00ffcc", "#ff3366"][i]
        st.markdown(f"<div style='border: 3px solid {color};' class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: {color};'>{hora}</h2>", unsafe_allow_html=True)
        if res:
            st.markdown(f"**Triple A:** {res[0]}<br>**Triple B:** {res[1]}<br>**Triple C:** {res[2]}", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color: #ccff00;'>⭐ {res[3].upper()} ⭐</h3>", unsafe_allow_html=True)
        else:
            st.write("Esperando...")
        st.markdown("</div>", unsafe_allow_html=True)

# Lógica de Sorteo (Simulada para Web)
if restante.total_seconds() <= 1:
    # Aquí se dispararía el sorteo automático
    st.rerun()

st.info("Esta página se actualiza automáticamente.")
