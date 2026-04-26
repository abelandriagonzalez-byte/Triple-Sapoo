import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    .titulo-top { font-size: 45px !important; color: #ccff00; font-weight: bold; margin-bottom: 0px; }
    .timer-digital { font-size: 50px !important; color: #ffffff; font-family: monospace; font-weight: bold; }
    .fecha-banner { 
        font-size: 24px; color: #ccff00; font-weight: bold; 
        border-top: 2px solid #ccff00; border-bottom: 2px solid #ccff00;
        padding: 5px; margin: 20px 0; background: #0b1a0b;
    }
    .hora-txt { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
    .res-linea { font-size: 22px; color: #ffffff; margin: 2px 0; font-family: 'Consolas', monospace; font-weight: bold; }
    .res-signo { font-size: 24px; color: #ccff00; font-weight: bold; margin-top: 5px; }
    .seccion-historial { color: #ccff00; font-size: 26px; font-weight: bold; margin-top: 50px; text-shadow: 2px 2px #000; }
    hr { border: 0; height: 1px; background: #ccff0044; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, a TEXT, b TEXT, c TEXT, signo TEXT)')
    return conn

def obtener_datos_dia(fecha, hora_etiqueta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha, hora_etiqueta))
    res = cursor.fetchone()
    conn.close()
    return res

# --- LÓGICA DE TIEMPO ---
ahora = datetime.now() - timedelta(hours=4) # VZLA
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]
horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]

# Contador
futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in horarios_metas]
futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
restante = int((min(futuros) - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #666;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo-top'>TRIPLE SAPO</div>", unsafe_allow_html=True)

h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #444; font-size: 14px; margin-top:-10px;'>PRÓXIMO SORTEO</p>", unsafe_allow_html=True)

# --- BLOQUE DE HOY ---
fecha_hoy = ahora.strftime("%Y-%m-%d")
st.markdown(f"<div class='fecha-banner'>📅 SORTEOS DE HOY: {ahora.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

cols_hoy = st.columns(3)
for i, h in enumerate(h_labels):
    with cols_hoy[i]:
        res = obtener_datos_dia(fecha_hoy, h)
        st.markdown(f"<div class='hora-txt' style='color:{['#ffcc00','#00ffcc','#ff3366'][i]}'>{h}</div>", unsafe_allow_html=True)
        if res:
            st.markdown(f"<div class='res-linea'>A: {res[0]}</div><div class='res-linea'>B: {res[1]}</div><div class='res-linea'>C: {res[2]}</div><div class='res-signo'>{res[3].upper()}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#444; font-style:italic;'>Esperando...</p>", unsafe_allow_html=True)

# --- HISTORIAL DE LOS ÚLTIMOS 5 DÍAS ---
st.markdown("<div class='seccion-historial'>📜 RESULTADOS ANTERIORES</div>", unsafe_allow_html=True)

for d in range(1, 6): # Revisa del día -1 al -5
    fecha_past = (ahora - timedelta(days=d)).strftime("%Y-%m-%d")
    fecha_bella = (ahora - timedelta(days=d)).strftime("%d/%m/%Y")
    
    st.markdown(f"<div class='fecha-banner' style='font-size:18px; margin: 10px 0;'>DÍA: {fecha_bella}</div>", unsafe_allow_html=True)
    
    cols_past = st.columns(3)
    for i, h in enumerate(h_labels):
        with cols_past[i]:
            res_p = obtener_datos_dia(fecha_past, h)
            st.markdown(f"<div style='font-size:16px; font-weight:bold; color:#aaa;'>{h}</div>", unsafe_allow_html=True)
            if res_p:
                st.markdown(f"<div style='font-size:14px;'>A: {res_p[0]}<br>B: {res_p[1]}<br>C: {res_p[2]}<br><b style='color:#ccff00'>{res_p[3].upper()}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:12px; color:#333;'>Sin sorteo</div>", unsafe_allow_html=True)
    st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)

# --- SORTEO AUTOMÁTICO ---
for idx, h_m in enumerate(horarios_metas):
    t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_s + timedelta(seconds=10)) and not obtener_datos_dia(fecha_hoy, h_labels[idx]):
        a, b, c = [f"{random.randint(0, 999):03d}" for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
