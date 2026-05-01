import streamlit as st
import sqlite3
import random
import pytz
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo para el reloj y animaciones
st_autorefresh(interval=1000, key="reloj_global")

# --- LÓGICA DE TIEMPO (VENEZUELA) ---
tz_vzla = pytz.timezone('America/Caracas')
ahora = datetime.now(tz_vzla)
fecha_hoy = ahora.strftime("%Y-%m-%d")

# Horarios exactos de los sorteos
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]
horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    .titulo-grande { font-size: 50px !important; color: #ccff00; font-weight: bold; text-shadow: 3px 3px 10px #000; margin-top: -10px; }
    .subtitulo-grande { font-size: 22px; color: #ffff00; letter-spacing: 3px; margin-bottom: 15px; }
    .timer-digital { font-size: 70px !important; color: #ffffff; font-family: 'Courier New', monospace; font-weight: bold; text-shadow: 0 0 20px #ccff00; }
    .fecha-banner { font-size: 24px; color: #ccff00; font-weight: bold; border-top: 3px solid #ccff00; border-bottom: 3px solid #ccff00; padding: 10px; margin: 20px 0; background: #0b1a0b; }
    .bola-tombola { 
        display: inline-block; width: 80px; height: 80px; line-height: 80px; 
        background: radial-gradient(circle at 30% 30%, #ffffff, #ccff00);
        color: #000; font-size: 30px; font-weight: bold; border-radius: 50%;
        margin: 10px; border: 3px solid #0b1a0b; box-shadow: 0 0 15px #ccff00;
    }
    .res-linea { font-size: 24px; color: #ffffff; font-weight: bold; margin: 5px 0; }
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

# --- CÁLCULO DE CUENTA REGRESIVA (Sincronizado) ---
futuros = []
for h in horarios_metas:
    hora_obj = datetime.strptime(h, "%H:%M:%S").time()
    dt_meta = datetime.combine(ahora.date(), hora_obj)
    dt_meta = tz_vzla.localize(dt_meta) # Localización forzada a Vzla
    if dt_meta <= ahora:
        dt_meta += timedelta(days=1)
    futuros.append(dt_meta)

proximo_sorteo = min(futuros)
restante = int((proximo_sorteo - ahora).total_seconds())
h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)

# --- NAVEGACIÓN ---
tab1, tab2 = st.tabs(["📺 MONITOR PRINCIPAL", "🎰 TÓMBOLA EN VIVO"])

with tab1:
    st.markdown("<div class='titulo-grande'>TRIPLE SAPO</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo-grande'>LOTERÍA DE MARA</div>", unsafe_allow_html=True)
    
    # Reloj Digital
    st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='fecha-banner'>📅 HOY: {ahora.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, h in enumerate(h_labels):
        with cols[i]:
            res = obtener_datos_dia(fecha_hoy, h)
            st.markdown(f"<h2 style='color:#ccff00'>{h}</h2>", unsafe_allow_html=True)
            if res:
                st.markdown(f"""
                    <div class='res-linea'>A: {res[0]}</div>
                    <div class='res-linea'>B: {res[1]}</div>
                    <div class='res-linea'>C: {res[2]}</div>
                    <div style='color:#ffff00; font-size:28px; font-weight:bold;'>{res[3].upper()}</div>
                """, unsafe_allow_html=True)
            else:
                st.info("Esperando...")

with tab2:
    st.markdown("## 🎰 SORTEO EN TIEMPO REAL")
    
    sorteo_activo = False
    for idx, h_m in enumerate(horarios_metas):
        t_s = datetime.strptime(h_m, "%H:%M:%S").replace(tzinfo=None) # Quitamos tz para combine
        t_s = tz_vzla.localize(datetime.combine(ahora.date(), t_s.time()))
        
        # El sorteo se activa visualmente 10 segundos antes y dura hasta 20 segundos después
        if (t_s - timedelta(seconds=10)) <= ahora <= (t_s + timedelta(seconds=20)) and not obtener_datos_dia(fecha_hoy, h_labels[idx]):
            sorteo_activo = True
            st.warning(f"¡ATENCIÓN! PREPARANDO SORTEO DE LAS {h_labels[idx]}")
            
            placeholder = st.empty()
            # Simulación de tómbola girando
            for _ in range(25):
                t_a, t_b, t_c = [f"{random.randint(0,999):03d}" for _ in range(3)]
                placeholder.markdown(f"""
                    <div style='display: flex; justify-content: center;'>
                        <div class='bola-tombola'>{t_a}</div>
                        <div class='bola-tombola'>{t_b}</div>
                        <div class='bola-tombola'>{t_c}</div>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(0.1)
            
            # Generar y guardar resultado definitivo
            a, b, c = [f"{random.randint(0,999):03d}" for _ in range(3)]
            z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
            
            with conectar_db() as db:
                db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
            
            st.balloons()
            st.success("¡SORTEO FINALIZADO!")
            time.sleep(3)
            st.rerun()

    if not sorteo_activo:
        st.write("La tómbola se activará automáticamente a la hora del sorteo.")
        st.markdown("<div style='opacity: 0.2;'><div class='bola-tombola'>?</div><div class='bola-tombola'>?</div><div class='bola-tombola'>?</div></div>", unsafe_allow_html=True)
