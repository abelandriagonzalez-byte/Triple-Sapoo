import streamlit as st
impoimport streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- ESTILOS CSS (DISEÑO VERTICAL Y LIMPIO) ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; text-align: center; }
    
    .titulo { font-size: 60px !important; color: #ccff00; font-weight: bold; margin-bottom: 0px; }
    .subtitulo { font-size: 20px; color: #ffff00; margin-top: -10px; margin-bottom: 20px; }
    .timer { font-size: 80px !important; color: #ffffff; font-family: monospace; font-weight: bold; }

    /* Estilos para la lista vertical */
    .contenedor-vertical {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .hora-txt { font-size: 38px; font-weight: bold; margin-bottom: 15px; }
    .resultado-linea { 
        font-size: 30px; 
        color: #ffffff; 
        margin: 5px 0; 
        font-family: 'Consolas', monospace;
        font-weight: bold;
    }
    .signo-txt { 
        font-size: 45px; 
        color: #ccff00; 
        font-weight: bold; 
        font-family: 'Arial Black'; 
        margin-top: 15px;
        text-shadow: 0 0 15px #ccff00;
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

# Calcular tiempo para el contador
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo_t = min(futuros)
segundos_faltantes = int((proximo_t - ahora).total_seconds())

# --- CABECERA ---
st.markdown(f"<p style='text-align: right; color: #666;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo'>TRIPLE SAPO</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>DE SU LOTERÍA DE MARA</div>", unsafe_allow_html=True)

# Contador
h_f, rem = divmod(segundos_faltantes, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- RESULTADOS DE HOY (FORMATO VERTICAL) ---
cols = st.columns(3)
colores = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos(fecha_hoy, h)
        # Título de la Hora
        st.markdown(f"<div class='hora-txt' style='color: {colores[i]};'>{h}</div>", unsafe_allow_html=True)
        
        if res:
            # Mostramos A, B, C y Signo uno debajo del otro (Vertical)
            st.markdown(f"""
                <div class='contenedor-vertical'>
                    <div class='resultado-linea'><b>A:</b> {res[0]}</div>
                    <div class='resultado-linea'><b>B:</b> {res[1]}</div>
                    <div class='resultado-linea'><b>C:</b> {res[2]}</div>
                    <div class='signo-txt'>⭐ {res[3].upper()} ⭐</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='espera'>Esperando sorteo...</div>", unsafe_allow_html=True)

# --- HISTORIAL DE AYER ---
st.write("---")
st.markdown("<p style='color: #444; font-size: 14px;'>HISTORIAL DÍA ANTERIOR</p>", unsafe_allow_html=True)
cols_ayer = st.columns(3)
for i, h in enumerate(h_labels):
    with cols_ayer[i]:
        r_a = obtener_datos(fecha_ayer, h)
        if r_a:
            st.markdown(f"<div style='color:#666; font-size:13px;'>{h}: {r_a[0]}-{r_a[1]}-{r_a[2]} ({r_a[3]})</div>", unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO (POR SI FALTA ALGUNO) ---
for idx, h_m in enumerate(horarios_metas):
    t_s = datetime.strptime(h_m, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_s + timedelta(seconds=10)) and not obtener_datos(fecha_hoy, h_labels[idx]):
        a, b, c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        conn = conectar_db()
        conn.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        conn.commit()
        conn.close()
        st.rerun()
rt sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Refresco cada 1 segundo
st_autorefresh(interval=1000, key="reloj_global")

# --- DISEÑO ATRACTIVO (ESTILO NEÓN) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1a0b; color: white; }
    
    .titulo-principal {
        font-size: 70px !important;
        color: #ccff00;
        text-align: center;
        font-weight: bold;
        text-shadow: 0 0 20px #ccff00;
        margin-bottom: 0px;
    }
    
    .subtitulo {
        font-size: 25px;
        color: #ffff00;
        text-align: center;
        margin-top: -10px;
        letter-spacing: 5px;
    }

    .timer-neon {
        font-size: 110px !important;
        color: #ffffff;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        text-shadow: 0 0 30px #ffffff;
    }

    .resultado-hora {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
    }

    .resultado-numeros {
        font-size: 35px;
        color: #ffffff;
        text-align: center;
        letter-spacing: 10px;
        margin: 10px 0;
    }

    .resultado-signo {
        font-size: 60px;
        color: #ccff00;
        font-weight: bold;
        text-align: center;
        text-shadow: 0 0 15px #ccff00;
        font-family: 'Arial Black';
    }

    .espera {
        font-size: 22px;
        color: #335533;
        text-align: center;
        font-style: italic;
    }
    
    hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, #ccff00, transparent); margin: 40px 0; }
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

# Próximo sorteo
futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo_t = min(futuros)
segundos_faltantes = int((proximo_t - ahora).total_seconds())

# --- INTERFAZ ---
st.markdown(f"<p style='text-align: right; color: #555;'>{ahora.strftime('%I:%M:%S %p')}</p>", unsafe_allow_html=True)
st.markdown("<div class='titulo-principal'>TRIPLE SAPO</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>LOTERÍA DE MARA</div>", unsafe_allow_html=True)

# Contador
h_f, rem = divmod(segundos_faltantes, 3600)
m_f, s_f = divmod(rem, 60)
st.markdown(f"<div class='timer-neon'>{h_f:02d}:{m_f:02d}:{s_f:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444;'>TIEMPO PARA EL PRÓXIMO SORTEO</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- RESULTADOS SIN CUADROS (ESTILO LIMPIO) ---
cols = st.columns(3)
colores_fuego = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos(fecha_hoy, h)
        # Título de la hora
        st.markdown(f"<div class='resultado-hora' style='color: {colores_fuego[i]};'>{h}</div>", unsafe_allow_html=True)
        
        if res:
            # Triples (res[0]=A, res[1]=B, res[2]=C)
            st.markdown(f"<div class='resultado-numeros'>{res[0]} - {res[1]} - {res[2]}</div>", unsafe_allow_html=True)
            # Signo
            st.markdown(f"<div class='resultado-signo'>⭐ {res[3].upper()} ⭐</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='espera'>Esperando sorteo...</div>", unsafe_allow_html=True)

# --- HISTORIAL AYER ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #333; font-size: 14px;'>HISTORIAL DÍA ANTERIOR</p>", unsafe_allow_html=True)
cols_a = st.columns(3)
for i, h in enumerate(h_labels):
    with cols_a[i]:
        res_a = obtener_datos(fecha_ayer, h)
        if res_a:
            st.markdown(f"<p style='text-align:center; color:#555; font-size:14px;'>{h}: {res_a[0]}-{res_a[1]}-{res_a[2]} ({res_a[3]})</p>", unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO ---
for idx, h_meta_str in enumerate(horarios_metas):
    t_m = datetime.strptime(h_meta_str, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if ahora > (t_m + timedelta(seconds=5)) and not obtener_datos(fecha_hoy, h_labels[idx]):
        a, b, c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        z = random.choice(["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"])
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", (fecha_hoy, h_labels[idx], a, b, c, z))
        st.rerun()
