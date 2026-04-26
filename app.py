import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS AJUSTADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    
    .titulo { font-size: 60px !important; color: #ccff00; font-weight: bold; margin-bottom: 0px; text-shadow: 2px 2px 10px #000; }
    .subtitulo { font-size: 20px; color: #ffff00; margin-top: -10px; margin-bottom: 20px; }
    .timer { font-size: 80px !important; color: #ffffff; font-family: monospace; font-weight: bold; }

    /* Estilos para los resultados verticales */
    .contenedor-vertical { 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        padding: 10px;
        width: 100%;
    }
    
    .hora-txt { 
        font-size: 32px; 
        font-weight: bold; 
        color: white;
        margin-bottom: 15px; 
        display: block; 
        text-align: center;
        width: 100%;
    }
    
    .res-linea { 
        font-size: 32px; 
        color: #ffffff; 
        margin: 5px 0; 
        font-family: 'Consolas', monospace; 
        font-weight: bold; 
    }
    
    .res-signo { 
        font-size: 40px; /* Tamaño disminuido */
        color: #ccff00; 
        font-weight: bold; 
        font-family: 'Arial Black'; 
        margin-top: 10px; 
        text-shadow: 0 0 10px #ccff00; 
    }
    
    .espera { font-size: 18px; color: #446644; font-style: italic; margin-top: 20px; }
    hr { border: 0; height: 1px; background: #ccff0033; margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, a TEXT, b TEXT, c TEXT, signo TEXT)')
    return conn

def obtener_datos(fecha, hora_etiqueta):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha, hora_etiqueta))
        res = cursor.fetchone()
        conn.close()
        return res
    except:
        return None

# --- TIEMPO VENEZUELA (UTC-4) ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")

horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]

# Cálculo de próximo sorteo
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo_t = min(futuros)
segundos_faltantes = int((proximo_t - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #666;'>VZLA: {ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo'>TRIPLE SAPO</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>DE SU LOTERÍA DE MARA</div>", unsafe_allow_html=True)

# Contador
h_f, rem = divmod(segundos_faltantes, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- RESULTADOS VERTICALES ---
cols = st.columns(3)
colores_h = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos(fecha_hoy, h)
        # La Hora ahora está forzada a centrarse sobre el contenedor
        st.markdown(f"<div class='hora-txt' style='border-bottom: 3px solid {colores_h[i]};'>{h}</div>", unsafe_allow_html=True)
        
        if res:
            # Mostramos A, B, C y Signo en vertical
            st.markdown(f"""
                <div class='contenedor-vertical'>
                    <div class='res-linea'>A: {res[0]}</div>
                    <div class='res-linea'>B: {res[1]}</div>
                    <div class='res-linea'>C: {res[2]}</div>
                    <div class='res-signo'>⭐ {res[3].upper()} ⭐</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='espera'>Esperando Sorteo...</div>", unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO ---
for idx, h_m in enumerate(horarios_metas):
    t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_s + timedelta(seconds=10)) and not obtener_datos(fecha_hoy, h_labels[idx]):
        a, b, c = [f"{random.randint(0, 999):03d}" for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
