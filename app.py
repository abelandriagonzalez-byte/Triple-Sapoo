import streamlit as st
import sqlite3
import random
impoimport streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS (SÓLO TEXTO Y COLORES) ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; }
    .timer-digital { font-size: 90px !important; color: #ccff00; text-align: center; font-weight: bold; font-family: 'Courier New'; }
    .hora-label { font-size: 35px; font-weight: bold; text-align: center; margin-top: 20px; }
    .triples-texto { font-size: 26px; text-align: center; margin: 10px 0; letter-spacing: 3px; color: #ffffff; }
    .signo-gigante { font-size: 55px; text-align: center; color: #ccff00; font-weight: bold; font-family: 'Arial Black'; margin-top: -10px; }
    .espera-texto { font-size: 22px; text-align: center; color: #558855; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, a TEXT, b TEXT, c TEXT, signo TEXT)')
    return conn

def obtener_datos(fecha, hora_etiqueta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha, hora_etiqueta))
    res = cursor.fetchone()
    conn.close()
    return res

# --- TIEMPO VENEZUELA (UTC-4) ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")
fecha_ayer = (ahora - timedelta(days=1)).strftime("%Y-%m-%d")

horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]

# Calcular próximo sorteo
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo_t = min(futuros)
segundos_faltantes = int((proximo_t - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #aaa; margin:0;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #ccff00; font-size: 65px; margin:0;'>TRIPLE SAPO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffff00; font-size: 22px;'>DE SU LOTERÍA DE MARA</p>", unsafe_allow_html=True)

# Contador
h_f, rem = divmod(segundos_faltantes, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-digital'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 20px; margin-top:-15px;'>PRÓXIMO SORTEO</p>", unsafe_allow_html=True)

st.write("---")

# --- MOSTRAR RESULTADOS (SIN CUADROS) ---
cols = st.columns(3)
colores_horas = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos(fecha_hoy, h)
        # 1. Mostrar la hora
        st.markdown(f"<p class='hora-label' style='color: {colores_horas[i]};'>{h}</p>", unsafe_allow_html=True)
        
        if res:
            # 2. Mostrar los números triples (A, B, C)
            st.markdown(f"<p class='triples-texto'>A: {res[0]} | B: {res[1]} | C: {res[2]}</p>", unsafe_allow_html=True)
            # 3. Mostrar el Signo en gigante
            st.markdown(f"<p class='signo-gigante'>⭐ {res[3].upper()} ⭐</p>", unsafe_allow_html=True)
        else:
            # 4. Texto de espera si no hay sorteo
            st.markdown("<p class='espera-texto'>Esperando resultados...</p>", unsafe_allow_html=True)

# --- HISTORIAL DE AYER (SIMPLIFICADO) ---
st.write("---")
st.markdown("<p style='text-align: center; color: #666; font-size: 18px;'>RESUMEN DÍA ANTERIOR</p>", unsafe_allow_html=True)
cols_a = st.columns(3)
for i, h in enumerate(h_labels):
    with cols_a[i]:
        res_a = obtener_datos(fecha_ayer, h)
        if res_a:
            st.markdown(f"<p style='text-align:center; color:#888; font-size:15px;'>{h}: <b>{res_a[0]}-{res_a[1]}-{res_a[2]}</b> ({res_a[3]})</p>", unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO (REFORZADA) ---
for idx, h_meta_str in enumerate(horarios_metas):
    t_m = datetime.strptime(h_meta_str, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_m + timedelta(seconds=5)) and not obtener_datos(fecha_hoy, h_labels[idx]):
        a, b, c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
rt time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo (Vital para el contador y la tómbola)
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; }
    
    /* Cuadros de Hoy */
    .card-sorteo { 
        background-color: #2d5a27; border-radius: 20px; text-align: center; 
        padding: 20px; min-height: 250px; border: 5px solid #ccff00;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    /* Cuadros de Ayer */
    .card-ayer { 
        background-color: #1e331b; border-radius: 20px; text-align: center; 
        padding: 15px; min-height: 180px; border: 2px solid #555;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .bola-animada { 
        background-color: white; color: #1a3c1a; border-radius: 50%; 
        width: 120px; height: 120px; display: flex; align-items: center; 
        justify-content: center; font-size: 65px; font-weight: bold; 
        border: 6px solid #ccff00; margin: auto; box-shadow: 0 0 30px #ccff00;
    }
    
    .timer-display { font-size: 100px !important; color: #ccff00; text-align: center; font-weight: bold; line-height: 1; }
    .status-envivo { color: #ff3366; font-size: 50px; font-weight: bold; text-align: center; animation: parpadeo 1s infinite; }
    @keyframes parpadeo { 0% {opacity: 1;} 50% {opacity: 0.3;} 100% {opacity: 1;} }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS resultados (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, a TEXT, b TEXT, c TEXT, signo TEXT)')
    return conn

def obtener_datos(fecha, hora_etiqueta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha, hora_etiqueta))
    res = cursor.fetchone()
    conn.close()
    return res

# --- LÓGICA DE TIEMPO (VENEZUELA UTC-4) ---
ahora = datetime.now() - timedelta(hours=4)
fecha_hoy = ahora.strftime("%Y-%m-%d")
fecha_ayer = (ahora - timedelta(days=1)).strftime("%Y-%m-%d")

horarios_metas = ["13:05:00", "17:05:00", "21:05:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:05 PM"]

# Calcular próximo sorteo
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo_t = min(futuros)
segundos_faltantes = int((proximo_t - ahora).total_seconds())

# --- INTERFAZ ---

# 1. TÓMBOLA EN VIVO (60 segundos antes)
if 0 <= segundos_faltantes <= 60:
    st.markdown("<h1 class='status-envivo'>🎰 SORTEO EN VIVO 🎰</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>Sorteo Programado: {proximo_t.strftime('%I:%M %p')}</h2>", unsafe_allow_html=True)
    cols_b = st.columns(3)
    for i in range(3):
        with cols_b[i]: st.markdown(f"<div class='bola-animada'>{random.randint(0, 9)}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 35px; margin-top: 30px;'>Extrayendo esferas en: <b>{segundos_faltantes}s</b></p>", unsafe_allow_html=True)
    
    if segundos_faltantes == 0:
        a, b, c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        label_h = h_labels[horarios_metas.index(proximo_t.strftime("%H:%M:%S"))]
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, label_h, a, b, c, z))
        st.balloons()
        time.sleep(2)
        st.rerun()
else:
    # 2. MONITOR PRINCIPAL
    st.markdown(f"<div style='text-align: right; font-family: monospace; font-size: 20px;'>{ahora.strftime('%I:%M:%S %p')}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #ccff00; font-size: 65px; margin-bottom:0;'>TRIPLE SAPO</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ffff00; font-size: 25px; margin-top:0;'>DE SU LOTERÍA DE MARA</h3>", unsafe_allow_html=True)

    horas, rem = divmod(segundos_faltantes, 3600)
    mins, segs = divmod(rem, 60)
    st.markdown(f"<div class='timer-display'>{horas:02d}:{mins:02d}:{segs:02d}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaa;'>PRÓXIMO SORTEO EN</p>", unsafe_allow_html=True)

    # RESULTADOS DE HOY
    st.write("---")
    st.markdown("<h2 style='text-align: center; color: white;'>SORTEOS DE HOY</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    colores = ["#ffcc00", "#00ffcc", "#ff3366"]
    for i, h in enumerate(h_labels):
        with cols[i]:
            res = obtener_datos(fecha_hoy, h)
            st.markdown(f"<div class='card-sorteo' style='border-color: {colores[i]};'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: {colores[i]}; margin-top: 0;'>{h}</h2>", unsafe_allow_html=True)
            if res:
                st.markdown(f"<p style='font-size: 22px; margin: 5px 0;'><b>A:</b> {res[0]} | <b>B:</b> {res[1]} | <b>C:</b> {res[2]}</p><h2 style='color: #ccff00; font-size: 35px;'>⭐ {res[3].upper()} ⭐</h2>", unsafe_allow_html=True)
            else: st.markdown("<p style='color: #666; font-size: 20px;'>Esperando sorteo...</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # RESULTADOS DE AYER (Cuadros completos)
    st.write("---")
    st.markdown("<h3 style='text-align: center; color: #888;'>RESULTADOS DEL DÍA ANTERIOR</h3>", unsafe_allow_html=True)
    cols_a = st.columns(3)
    for i, h in enumerate(h_labels):
        with cols_a[i]:
            res_a = obtener_datos(fecha_ayer, h)
            st.markdown(f"<div class='card-ayer'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color: #888; margin: 0;'>{h}</h4>", unsafe_allow_html=True)
            if res_a:
                st.markdown(f"<p style='font-size: 18px; margin: 5px 0;'>A:{res_a[0]} B:{res_a[1]} C:{res_a[2]}</p><b style='color: #ffff00;'>{res_a[3].upper()}</b>", unsafe_allow_html=True)
            else: st.markdown("<p style='color: #444; margin: 5px 0;'>Sin registros</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- SORTEO RETROACTIVO ---
for idx, h_meta_str in enumerate(horarios_metas):
    t_m = datetime.strptime(h_meta_str, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_m + timedelta(seconds=10)) and not obtener_datos(fecha_hoy, h_labels[idx]):
        a, b, c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db: db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
