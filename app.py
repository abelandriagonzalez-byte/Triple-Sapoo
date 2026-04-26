import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    .titulo { font-size: 38px !important; color: #ccff00; font-weight: bold; margin-bottom: 0px; }
    .fecha-hoy { font-size: 20px; color: #ffffff; margin-bottom: 10px; background: #0b1a0b; display: inline-block; padding: 5px 15px; border-radius: 8px; border: 1px solid #ccff00; }
    .timer-digital { font-size: 50px !important; color: #ffffff; font-family: monospace; font-weight: bold; text-shadow: 0 0 10px #ffffff; }
    .hora-txt { font-size: 24px; font-weight: bold; margin-bottom: 8px; border-bottom: 2px solid; padding-bottom: 3px; }
    .res-linea { font-size: 22px; color: #ffffff; margin: 2px 0; font-family: 'Consolas', monospace; font-weight: bold; }
    .res-signo { font-size: 26px; color: #ccff00; font-weight: bold; margin-top: 5px; }
    hr { border: 0; height: 1px; background: #ccff0033; margin: 20px 0; }
    .historial-box { text-align: left; background: #00000044; padding: 10px; border-radius: 10px; font-size: 13px; color: #ddd; margin-top: 5px; border-left: 4px solid #ccff00; }
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

def obtener_historial():
    conn = conectar_db()
    cursor = conn.cursor()
    # Trae los últimos 5 sorteos guardados
    cursor.execute("SELECT fecha, hora, a, b, c, signo FROM resultados ORDER BY id DESC LIMIT 5")
    res = cursor.fetchall()
    conn.close()
    return res

# --- TIEMPO VENEZUELA (UTC-4) ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")
fecha_pantalla = ahora.strftime("%d / %m / %Y")

horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]

futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

restante = int((min(futuros) - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #666; font-size: 12px;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo'>TRIPLE SAPO</div>", unsafe_allow_html=True)

# FECHA ACTUAL
st.markdown(f"<div class='fecha-hoy'>📅 {fecha_pantalla}</div>", unsafe_allow_html=True)

# CONTADOR
h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='color: #444; font-size: 14px; margin-top:-10px;'>PRÓXIMO SORTEO</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# RESULTADOS VERTICALES
cols = st.columns(3)
colores = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_hoy(fecha_hoy, h)
        st.markdown(f"<div class='hora-txt' style='color: {colores[i]}; border-color: {colores[i]};'>{h}</div>", unsafe_allow_html=True)
        if res:
            st.markdown(f"""<div style='display: flex; flex-direction: column; align-items: center;'>
                <div class='res-linea'>A: {res[0]}</div>
                <div class='res-linea'>B: {res[1]}</div>
                <div class='res-linea'>C: {res[2]}</div>
                <div class='res-signo'>{res[3].upper()}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #444; font-size: 14px;'>Esperando...</p>", unsafe_allow_html=True)

# SECCIÓN DE HISTORIAL (Últimos 5)
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left; color: #ccff00; font-weight: bold;'>📜 ÚLTIMOS 5 SORTEOS:</p>", unsafe_allow_html=True)

historial = obtener_historial()
for r in historial:
    st.markdown(f"""<div class='historial-box'>
        <b>{r[0]}</b> | {r[1]} <br>
        A:{r[2]} B:{r[3]} C:{r[4]} | <span style='color:#ccff00'>{r[5].upper()}</span>
    </div>""", unsafe_allow_html=True)

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
