import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo (Vital para el reloj y sorteos)
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    [data-testid="stImage"] { background-color: transparent !important; display: flex; justify-content: center; }
    .titulo-grande { font-size: 50px !important; color: #ccff00; font-weight: bold; text-shadow: 3px 3px 10px #000; margin-top: -10px; }
    .subtitulo-grande { font-size: 22px; color: #ffff00; letter-spacing: 3px; margin-bottom: 15px; }
    .timer-digital { font-size: 60px !important; color: #ffffff; font-family: monospace; font-weight: bold; text-shadow: 0 0 15px #ccff00; }
    .fecha-banner { font-size: 24px; color: #ccff00; font-weight: bold; border-top: 3px solid #ccff00; border-bottom: 3px solid #ccff00; padding: 10px; margin: 25px 0; background: #0b1a0b; }
    .hora-txt { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .res-linea { font-size: 26px; color: #ffffff; margin: 4px 0; font-family: 'Consolas', monospace; font-weight: bold; }
    .res-signo { font-size: 32px; color: #ccff00; font-weight: bold; margin-top: 8px; }
    .seccion-historial { color: #ccff00; font-size: 28px; font-weight: bold; margin-top: 50px; text-decoration: underline; }
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

# --- LÓGICA DE TIEMPO (VENEZUELA UTC-4) ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]
horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]

# Contador regresivo
futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in horarios_metas]
futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
restante = int((min(futuros) - ahora).total_seconds())

# --- CABECERA ---
try:
    st.image("logo.png", width=350)
except:
    pass

st.markdown("<div class='titulo-grande'>TRIPLE SAPO</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo-grande'>LOTERÍA DE MARA</div>", unsafe_allow_html=True)

h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)

# --- RESULTADOS DE HOY ---
st.markdown(f"<div class='fecha-banner'>📅 HOY: {ahora.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

cols_hoy = st.columns(3)
for i, h in enumerate(h_labels):
    with cols_hoy[i]:
        res = obtener_datos_dia(fecha_hoy, h)
        st.markdown(f"<div class='hora-txt' style='color:{['#ffcc00','#00ffcc','#ff3366'][i]}'>{h}</div>", unsafe_allow_html=True)
        if res:
            st.markdown(f"<div class='res-linea'>A: {res[0]}</div><div class='res-linea'>B: {res[1]}</div><div class='res-linea'>C: {res[2]}</div><div class='res-signo'>{res[3].upper()}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#444; font-style:italic; font-size:16px;'>Esperando...</p>", unsafe_allow_html=True)

# --- HISTORIAL AUTOMÁTICO (Días pasados) ---
st.markdown("<div class='seccion-historial'>📜 ÚLTIMOS RESULTADOS ANTERIORES</div>", unsafe_allow_html=True)

for d in range(1, 6): # Ayer (1) hasta hace 5 días
    fecha_past = (ahora - timedelta(days=d)).strftime("%Y-%m-%d")
    fecha_visual = (ahora - timedelta(days=d)).strftime("%d/%m/%Y")
    
    # Revisar si hay algún dato ese día antes de poner el banner
    res_check = obtener_datos_dia(fecha_past, h_labels[0]) or obtener_datos_dia(fecha_past, h_labels[1]) or obtener_datos_dia(fecha_past, h_labels[2])
    
    if res_check:
        st.markdown(f"<div class='fecha-banner' style='font-size:18px; margin: 10px 0;'>DÍA: {fecha_visual}</div>", unsafe_allow_html=True)
        cols_p = st.columns(3)
        for i, h in enumerate(h_labels):
            with cols_p[i]:
                rp = obtener_datos_dia(fecha_past, h)
                if rp:
                    st.markdown(f"<div style='font-size:14px; font-weight:bold; color:#aaa;'>{h}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:14px;'>A:{rp[0]} B:{rp[1]} C:{rp[2]}<br><b style='color:#ccff00'>{rp[3].upper()}</b></div>", unsafe_allow_html=True)

# --- SORTEO AUTOMÁTICO ---
for idx, h_m in enumerate(horarios_metas):
    t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_s + timedelta(seconds=10)) and not obtener_datos_dia(fecha_hoy, h_labels[idx]):
        a, b, c = [f"{random.randint(0,999):03d}" for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
