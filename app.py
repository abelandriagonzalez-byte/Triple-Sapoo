import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS UNIFICADOS ---
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

    /* Estilo de columna de resultados (Alineación vertical) */
    .contenedor-vertical { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px; }
    .hora-txt { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .res-linea { font-size: 24px; color: #ffffff; margin: 2px 0; font-family: 'Consolas', monospace; font-weight: bold; }
    .res-signo { font-size: 28px; color: #ccff00; font-weight: bold; margin-top: 5px; text-shadow: 0 0 8px #ccff00; }
    
    .seccion-titulo { text-align: left; color: #ccff00; font-size: 22px; font-weight: bold; margin-top: 40px; border-left: 5px solid #ccff00; padding-left: 10px; }
    hr { border: 0; height: 1px; background: #ccff0033; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, a TEXT, b TEXT, c TEXT, signo TEXT)')
    return conn

def obtener_hoy(fecha, hora_etiqueta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha, hora_etiqueta))
    res = cursor.fetchone()
    conn.close()
    return res

def obtener_historial_completo():
    conn = conectar_db()
    cursor = conn.cursor()
    # Trae los últimos 5 sorteos
    cursor.execute("SELECT fecha, hora, a, b, c, signo FROM resultados ORDER BY id DESC LIMIT 5")
    res = cursor.fetchall()
    conn.close()
    return res

# --- TIEMPO VENEZUELA ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")
fecha_pantalla = ahora.strftime("%d / %m / %Y")

horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]

futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in horarios_metas]
futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
restante = int((min(futuros) - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #666; font-size: 12px;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo-top'>TRIPLE SAPO</div>", unsafe_allow_html=True)

# CONTADOR
h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #444; font-size: 14px; margin-top:-10px;'>PRÓXIMO SORTEO</p>", unsafe_allow_html=True)

# FECHA ACTUAL ARRIBA DE LOS SORTEOS
st.markdown(f"<div class='fecha-banner'>SORTEOS DEL DÍA: {fecha_pantalla}</div>", unsafe_allow_html=True)

# RESULTADOS DE HOY (Columnas verticales)
cols = st.columns(3)
colores = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_hoy(fecha_hoy, h)
        st.markdown(f"<div class='hora-txt' style='color: {colores[i]};'>{h}</div>", unsafe_allow_html=True)
        if res:
            st.markdown(f"""<div class='contenedor-vertical'>
                <div class='res-linea'>A: {res[0]}</div>
                <div class='res-linea'>B: {res[1]}</div>
                <div class='res-linea'>C: {res[2]}</div>
                <div class='res-signo'>{res[3].upper()}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #444; font-style: italic;'>Esperando...</p>", unsafe_allow_html=True)

# --- HISTORIAL CON LA MISMA FORMA ---
st.markdown("<div class='seccion-titulo'>📜 HISTORIAL RECIENTE</div>", unsafe_allow_html=True)

historial = obtener_historial_completo()
if historial:
    for item in historial:
        # Cada fila del historial imita la forma de arriba
        st.markdown(f"<p style='text-align: left; color: #888; margin-bottom: 0;'>Fecha: {item[0]}</p>", unsafe_allow_html=True)
        h_col1, h_col2, h_col3, h_col4 = st.columns([1,1,1,1])
        with h_col1: st.markdown(f"<b style='color:#ccff00'>{item[1]}</b>", unsafe_allow_html=True)
        with h_col2: st.markdown(f"A: {item[2]}", unsafe_allow_html=True)
        with h_col3: st.markdown(f"B: {item[3]}", unsafe_allow_html=True)
        with h_col4: st.markdown(f"C: {item[4]} | <span style='color:#ccff00'>{item[5].upper()}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)

# --- SORTEO AUTOMÁTICO ---
for idx, h_m in enumerate(horarios_metas):
    t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_s + timedelta(seconds=10)) and not obtener_hoy(fecha_hoy, h_labels[idx]):
        a, b, c = [f"{random.randint(0, 999):03d}" for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        conn = conectar_db()
        conn.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        conn.commit(); conn.close()
        st.rerun()
