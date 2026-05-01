import streamlit as st
import sqlite3
import random
import pytz
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo para el reloj
st_autorefresh(interval=1000, key="reloj_global")

# --- LÓGICA DE TIEMPO (VENEZUELA) ---
tz_vzla = pytz.timezone('America/Caracas')
ahora = datetime.now(tz_vzla)
fecha_hoy = ahora.strftime("%Y-%m-%d")

h_labels = ["01:05 PM", "05:05 PM", "10:36 PM"]
horarios_metas = ["13:05:00", "17:05:00", "22:36:00"]

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    .titulo-grande { font-size: 50px !important; color: #ccff00; font-weight: bold; text-shadow: 3px 3px 10px #000; }
    .timer-digital { font-size: 60px !important; color: #ffffff; font-family: monospace; font-weight: bold; text-shadow: 0 0 15px #ccff00; }
    .bola-tombola { 
        display: inline-block; width: 100px; height: 100px; line-height: 100px; 
        background: radial-gradient(circle at 30% 30%, #ffffff, #ccff00);
        color: #000; font-size: 40px; font-weight: bold; border-radius: 50%;
        margin: 10px; border: 4px solid #0b1a0b; box-shadow: 0 0 20px #ccff00;
    }
    .fecha-banner { font-size: 24px; color: #ccff00; font-weight: bold; border-top: 3px solid #ccff00; border-bottom: 3px solid #ccff00; padding: 10px; margin: 20px 0; background: #0b1a0b; }
    .res-linea { font-size: 26px; color: #ffffff; font-weight: bold; }
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

# --- SISTEMA DE NAVEGACIÓN (VENTANAS) ---
tab1, tab2 = st.tabs(["📺 MONITOR PRINCIPAL", "🎰 TÓMBOLA EN VIVO"])

with tab1:
    st.markdown("<div class='titulo-grande'>TRIPLE SAPO</div>", unsafe_allow_html=True)
    
    # Cuenta Regresiva
    futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day, tzinfo=tz_vzla) for h in horarios_metas]
    futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
    restante = int((min(futuros) - ahora).total_seconds())
    h_f, rem = divmod(restante, 3600)
    m_f, s_f = divmod(rem, 60)
    st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='fecha-banner'>📅 HOY: {ahora.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, h in enumerate(h_labels):
        with cols[i]:
            res = obtener_datos_dia(fecha_hoy, h)
            st.markdown(f"### {h}")
            if res:
                st.markdown(f"<div class='res-linea'>A: {res[0]}</div><div class='res-linea'>B: {res[1]}</div><div class='res-linea'>C: {res[2]}</div><div style='color:#ccff00; font-size:30px;'>{res[3].upper()}</div>", unsafe_allow_html=True)
            else:
                st.info("Esperando...")

with tab2:
    st.markdown("## 🎰 SIMULACIÓN DE LA TÓMBOLA")
    
    # Revisar si es hora de un sorteo
    sorteo_activo = False
    for idx, h_m in enumerate(horarios_metas):
        t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day, tzinfo=tz_vzla)
        
        # Si estamos en el rango de los primeros 15 segundos después de la hora
        if t_s <= ahora <= (t_s + timedelta(seconds=15)) and not obtener_datos_dia(fecha_hoy, h_labels[idx]):
            sorteo_activo = True
            st.warning(f"¡INICIANDO SORTEO DE LAS {h_labels[idx]}!")
            
            # Efecto Tómbola (Animación)
            placeholder = st.empty()
            for _ in range(20): # 20 cambios rápidos
                temp_a, temp_b, temp_c = [f"{random.randint(0,999):03d}" for _ in range(3)]
                placeholder.markdown(f"""
                    <div style='display: flex; justify-content: center;'>
                        <div class='bola-tombola'>{temp_a}</div>
                        <div class='bola-tombola'>{temp_b}</div>
                        <div class='bola-tombola'>{temp_c}</div>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(0.1)
            
            # Guardar resultado final
            a, b, c = [f"{random.randint(0,999):03d}" for _ in range(3)]
            z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
            
            with conectar_db() as db:
                db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
            
            st.balloons()
            st.success(f"¡RESULTADO FINAL REGISTRADO!")
            time.sleep(2)
            st.rerun()

    if not sorteo_activo:
        st.write("La tómbola se activará automáticamente a la hora del sorteo.")
        st.markdown("""
            <div style='opacity: 0.3;'>
                <div class='bola-tombola'>?</div><div class='bola-tombola'>?</div><div class='bola-tombola'>?</div>
            </div>
        """, unsafe_allow_html=True)
