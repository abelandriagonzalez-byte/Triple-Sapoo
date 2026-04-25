import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Motor de refresco automático cada 1 segundo
st_autorefresh(interval=1000, key="reloj_refresco")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; }
    .card { background-color: #2d5a27; border-radius: 15px; text-align: center; padding: 20px; min-height: 200px; }
    .timer { font-size: 100px !important; font-family: 'Consolas', monospace; color: #ccff00; text-align: center; font-weight: bold; margin-top: -20px; }
    .reloj-actual { font-size: 25px; color: white; text-align: right; font-family: 'Consolas'; }
    h1, h3 { text-align: center; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, 
                    a TEXT, b TEXT, c TEXT, signo TEXT)''')
    return conn

conn = conectar_db()

def obtener_datos_hoy(hora_etiqueta):
    # Ajuste de hora Venezuela (UTC-4)
    ahora_ven = datetime.now() - timedelta(hours=4)
    fecha_hoy = ahora_ven.strftime("%Y-%m-%d")
    cursor = conn.cursor()
    cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha_hoy, hora_etiqueta))
    return cursor.fetchone()

# --- LÓGICA DE TIEMPO (VENEZUELA) ---
ahora = datetime.now() - timedelta(hours=4)

# Cabecera con Reloj en la esquina
col_t1, col_t2 = st.columns([3, 1])
with col_t2:
    st.markdown(f"<div class='reloj-actual'>{ahora.strftime('%I:%M:%S %p')}</div>", unsafe_allow_html=True)

st.markdown("<h1 style='color: #ccff00;'>TRIPLE SAPO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #ffff00;'>DE SU LOTERÍA DE MARA</h3>", unsafe_allow_html=True)

# Horarios de los sorteos
horarios_metas = ["13:05:00", "17:05:00", "21:58:00"]
h_labels = ["01:05 PM", "05:05 PM", "09:58 PM"]

# Cálculo de Próximo Sorteo para el contador
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo = min(futuros)
restante = proximo - ahora
segundos_faltantes = int(restante.total_seconds())

# Formatear el contador HH:MM:SS
horas, rem = divmod(segundos_faltantes, 3600)
minutos, segundos = divmod(rem, 60)
tiempo_display = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

st.markdown(f"<div class='timer'>{tiempo_display}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'>PRÓXIMO SORTEO EN</p>", unsafe_allow_html=True)

# --- TABLERO DE RESULTADOS ---
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(3)
colores = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos_hoy(h)
        st.markdown(f"<div style='border: 4px solid {colores[i]};' class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: {colores[i]};'>{h}</h2>", unsafe_allow_html=True)
        
        if res:
            st.markdown(f"<p style='font-size: 22px;'>A: {res[0]} | B: {res[1]} | C: {res[2]}</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #ccff00;'>⭐ {res[3].upper()} ⭐</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 20px; color: #888;'>Esperando...</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO (RETROACTIVO) ---
for idx, h_meta in enumerate(horarios_metas):
    t_sorteo = datetime.strptime(h_meta, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    label_actual = h_labels[idx]
    
    # Si ya pasó la hora del sorteo y NO hay resultado en la DB
    if ahora >= t_sorteo and not obtener_datos_hoy(label_actual):
        a = "".join([str(random.randint(0, 9)) for _ in range(3)])
        b = "".join([str(random.randint(0, 9)) for _ in range(3)])
        c = "".join([str(random.randint(0, 9)) for _ in range(3)])
        signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        z = random.choice(signos)
        
        fecha_str = ahora.strftime("%Y-%m-%d")
        with conectar_db() as database:
            database.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", 
                           (fecha_str, label_actual, a, b, c, z))
            database.commit()
        
        st.balloons()
        st.rerun()

st.sidebar.info("Ajuste de hora: Venezuela (UTC-4)")
