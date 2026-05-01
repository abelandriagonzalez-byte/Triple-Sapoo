import streamlit as st
import sqlite3
import random
import pytz
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- LÓGICA DE TIEMPO (VENEZUELA) ---
tz_vzla = pytz.timezone('America/Caracas')
ahora = datetime.now(tz_vzla)
fecha_hoy = ahora.strftime("%Y-%m-%d")

h_labels = ["01:05 PM", "05:05 PM", "10:49 PM"]
horarios_metas = ["13:05:00", "17:05:00", "22:49:00"]

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    .titulo-grande { font-size: 50px !important; color: #ccff00; font-weight: bold; text-shadow: 3px 3px 10px #000; }
    .timer-digital { font-size: 70px !important; color: #ffffff; font-family: monospace; font-weight: bold; text-shadow: 0 0 20px #ccff00; }
    .bola-tombola { 
        display: inline-block; width: 100px; height: 100px; line-height: 100px; 
        background: radial-gradient(circle at 30% 30%, #ffffff, #ccff00);
        color: #000; font-size: 38px; font-weight: bold; border-radius: 50%;
        margin: 15px; border: 4px solid #0b1a0b; box-shadow: 0 0 25px #ccff00;
    }
    .bola-signo { 
        display: inline-block; padding: 10px 30px; background: #ffff00; 
        color: #000; font-size: 30px; font-weight: bold; border-radius: 20px;
        margin-top: 20px; border: 3px solid #000; box-shadow: 0 0 15px #ffff00;
    }
    .letra-label { font-size: 25px; color: #ccff00; font-weight: bold; margin-bottom: -10px; }
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

# --- CUENTA REGRESIVA ---
futuros = []
for h in horarios_metas:
    h_dt = tz_vzla.localize(datetime.combine(ahora.date(), datetime.strptime(h, "%H:%M:%S").time()))
    if h_dt <= ahora: h_dt += timedelta(days=1)
    futuros.append(h_dt)
restante = int((min(futuros) - ahora).total_seconds())
h_f, rem = divmod(restante, 3600)
m_f, s_f = divmod(rem, 60)

# --- NAVEGACIÓN ---
tab1, tab2 = st.tabs(["📺 MONITOR PRINCIPAL", "🎰 TÓMBOLA EN VIVO"])

with tab1:
    st.markdown("<div class='titulo-grande'>TRIPLE SAPO</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, h in enumerate(h_labels):
        with cols[i]:
            res = obtener_datos_dia(fecha_hoy, h)
            st.markdown(f"<h3 style='color:#ccff00'>{h}</h3>", unsafe_allow_html=True)
            if res:
                st.markdown(f"**A:** {res[0]}<br>**B:** {res[1]}<br>**C:** {res[2]}<br><b style='color:#ffff00'>{res[3].upper()}</b>", unsafe_allow_html=True)
            else: st.info("Esperando...")

with tab2:
    st.markdown("## 🎰 SORTEO INDIVIDUAL POR LETRAS")
    btn_prueba = st.button("🚀 INICIAR SIMULACIÓN LENTA")
    
    if 'sorteo_ejecutado' not in st.session_state:
        st.session_state.sorteo_ejecutado = None

    sorteo_activo = False
    for idx, h_m in enumerate(horarios_metas):
        t_sorteo = tz_vzla.localize(datetime.combine(ahora.date(), datetime.strptime(h_m, "%H:%M:%S").time()))
        es_hora = t_sorteo <= ahora <= (t_sorteo + timedelta(seconds=30)) and not obtener_datos_dia(fecha_hoy, h_labels[idx])
        
        if (es_hora and st.session_state.sorteo_ejecutado != h_labels[idx]) or btn_prueba:
            sorteo_activo = True
            
            # Resultados finales que se revelarán
            final_a, final_b, final_c = [f"{random.randint(0,999):03d}" for _ in range(3)]
            final_z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
            
            display_a, display_b, display_c, display_z = "???", "???", "???", "???"
            placeholder = st.empty()

            # SECUENCIA LENTA DE REVELACIÓN
            pasos = [("A", 25), ("B", 25), ("C", 25), ("Z", 35)]
            
            for fase, vueltas in pasos:
                for _ in range(vueltas):
                    # Mientras gira la fase actual, las demás muestran valores aleatorios o fijos
                    if fase == "A": display_a = f"{random.randint(0,999):03d}"
                    elif fase == "B": display_b = f"{random.randint(0,999):03d}"
                    elif fase == "C": display_c = f"{random.randint(0,999):03d}"
                    elif fase == "Z": display_z = random.choice(["???", "Leo", "Aries", "Piscis", "Tauro"])

                    placeholder.markdown(f"""
                        <div style='display: flex; justify-content: center; gap: 20px;'>
                            <div><div class='letra-label'>TRIPLE A</div><div class='bola-tombola'>{display_a}</div></div>
                            <div><div class='letra-label'>TRIPLE B</div><div class='bola-tombola'>{display_b}</div></div>
                            <div><div class='letra-label'>TRIPLE C</div><div class='letra-label'>TRIPLE C</div><div class='bola-tombola'>{display_c}</div></div>
                        </div>
                        <div class='bola-signo'>{display_z.upper()}</div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.08) # Velocidad del giro
                
                # Al terminar las vueltas de una fase, fijamos su valor real
                if fase == "A": display_a = final_a
                elif fase == "B": display_b = final_b
                elif fase == "C": display_c = final_c
                elif fase == "Z": display_z = final_z

            # Guardar si es real
            if not btn_prueba:
                with conectar_db() as db:
                    db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], final_a, final_b, final_c, final_z))
                st.session_state.sorteo_ejecutado = h_labels[idx]
            
            st.balloons()
            time.sleep(4)
            st.rerun()
            break

    if not sorteo_activo:
        st.write("Esperando hora de sorteo para iniciar secuencia...")
        st.markdown("<div style='opacity: 0.2; filter: grayscale(1);'><div class='bola-tombola'>000</div><div class='bola-tombola'>000</div><div class='bola-tombola'>000</div><br><div class='bola-signo'>SIGNO</div></div>", unsafe_allow_html=True)
