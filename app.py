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

# --- LÓGICA DE TIEMPO ---
tz_vzla = pytz.timezone('America/Caracas')
ahora = datetime.now(tz_vzla)
fecha_hoy = ahora.strftime("%Y-%m-%d")

h_labels = ["01:05 PM", "05:05 PM", "10:53 PM"]
horarios_metas = ["13:05:00", "17:05:00", "22:53:00"]

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
        display: inline-block; padding: 15px 40px; background: #ffff00; 
        color: #000; font-size: 32px; font-weight: bold; border-radius: 20px;
        margin-top: 20px; border: 3px solid #000; box-shadow: 0 0 15px #ffff00;
    }
    .letra-label { font-size: 22px; color: #ccff00; font-weight: bold; margin-bottom: -10px; }
    .fase-activa { border: 5px solid #ffffff !important; transform: scale(1.1); transition: 0.3s; }
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
            st.markdown(f"### {h}")
            if res:
                st.markdown(f"**A:** {res[0]}<br>**B:** {res[1]}<br>**C:** {res[2]}<br><b style='color:#ccff00'>{res[3].upper()}</b>", unsafe_allow_html=True)
            else: st.info("Esperando...")

with tab2:
    st.markdown("## 🎰 SORTEO SECUENCIAL")
    btn_prueba = st.button("🚀 INICIAR TÓMBOLA (PRUEBA)")
    
    if 'sorteo_ejecutado' not in st.session_state:
        st.session_state.sorteo_ejecutado = None

    sorteo_activo = False
    for idx, h_m in enumerate(horarios_metas):
        t_sorteo = tz_vzla.localize(datetime.combine(ahora.date(), datetime.strptime(h_m, "%H:%M:%S").time()))
        es_hora = t_sorteo <= ahora <= (t_sorteo + timedelta(seconds=45)) and not obtener_datos_dia(fecha_hoy, h_labels[idx])
        
        if (es_hora and st.session_state.sorteo_ejecutado != h_labels[idx]) or btn_prueba:
            sorteo_activo = True
            
            # 1. Generar resultados finales
            final_a = f"{random.randint(0,999):03d}"
            final_b = f"{random.randint(0,999):03d}"
            final_c = f"{random.randint(0,999):03d}"
            final_z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
            
            # Variables de visualización
            v_a, v_b, v_c, v_z = "???", "???", "???", "ESPERANDO"
            placeholder = st.empty()

            # --- ANIMACIÓN POR FASES ---
            fases = [("A", final_a), ("B", final_b), ("C", final_c), ("Z", final_z)]
            
            for nombre_fase, valor_final in fases:
                # Cada fase gira durante 3 segundos (30 iteraciones de 0.1s)
                for _ in range(30):
                    if nombre_fase == "A": v_a = f"{random.randint(0,999):03d}"
                    elif nombre_fase == "B": v_b = f"{random.randint(0,999):03d}"
                    elif nombre_fase == "C": v_c = f"{random.randint(0,999):03d}"
                    elif nombre_fase == "Z": v_z = random.choice(["Aries", "Leo", "Virgo", "Piscis", "Tauro"])

                    # Dibujar estado actual
                    placeholder.markdown(f"""
                        <div style='display: flex; justify-content: center; gap: 20px;'>
                            <div><div class='letra-label'>TRIPLE A</div><div class='bola-tombola {"fase-activa" if nombre_fase=="A" else ""}'>{v_a}</div></div>
                            <div><div class='letra-label'>TRIPLE B</div><div class='bola-tombola {"fase-activa" if nombre_fase=="B" else ""}'>{v_b}</div></div>
                            <div><div class='letra-label'>TRIPLE C</div><div class='bola-tombola {"fase-activa" if nombre_fase=="C" else ""}'>{v_c}</div></div>
                        </div>
                        <div class='bola-signo {"fase-activa" if nombre_fase=="Z" else ""}'>{v_z.upper()}</div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.08)
                
                # Al terminar el giro de la fase, fijamos el valor real
                if nombre_fase == "A": v_a = valor_final
                elif nombre_fase == "B": v_b = valor_final
                elif nombre_fase == "C": v_c = valor_final
                elif nombre_fase == "Z": v_z = valor_final

            # --- GUARDADO Y FINALIZACIÓN ---
            if not btn_prueba:
                with conectar_db() as db:
                    db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", 
                               (fecha_hoy, h_labels[idx], final_a, final_b, final_c, final_z))
                st.session_state.sorteo_ejecutado = h_labels[idx]
                st.success(f"SORTEO {h_labels[idx]} GUARDADO")
            
            st.balloons()
            time.sleep(5)
            st.rerun()
            break

    if not sorteo_activo:
        st.write("Tómbola lista para el próximo sorteo.")
        st.markdown("<div style='opacity: 0.3;'><div class='bola-tombola'>???</div><div class='bola-tombola'>???</div><div class='bola-tombola'>???</div><br><div class='bola-signo'>ESPERANDO...</div></div>", unsafe_allow_html=True)
