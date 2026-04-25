import streamlit as st
import sqlite3
import random
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Triple Sapo - Monitor Oficial", layout="wide")

# Motor de refresco automático cada 1 segundo para el reloj y contador
st_autorefresh(interval=1000, key="reloj_refresco")

# --- ESTILOS VISUALES TOTALES ---
st.markdown("""
    <style>
    .stApp { background-color: #1a3c1a; color: white; }
    
    /* Contenedor del Cuadro */
    .card-sorteo {
        background-color: #2d5a27;
        border-radius: 20px;
        text-align: center;
        padding: 20px;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .timer-grande { 
        font-size: 90px !important; 
        font-family: 'Consolas', monospace; 
        color: #ccff00; 
        text-align: center; 
        font-weight: bold; 
        line-height: 1;
        margin-bottom: 0px;
    }
    
    .reloj-esquina { 
        font-size: 22px; 
        color: white; 
        text-align: right; 
        font-family: 'Consolas'; 
        padding-right: 20px;
    }
    
    .titulo-principal {
        color: #ccff00;
        font-family: 'Arial Black';
        text-align: center;
        font-size: 50px;
        margin-top: -30px;
    }
    
    .subtitulo {
        color: #ffff00;
        text-align: center;
        font-size: 20px;
        font-style: italic;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect("sorteos_web.db", check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora TEXT, 
                    a TEXT, b TEXT, c TEXT, signo TEXT)''')
    return conn

def obtener_datos_hoy(hora_etiqueta):
    ahora_ven = datetime.now() - timedelta(hours=4)
    fecha_hoy = ahora_ven.strftime("%Y-%m-%d")
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT a, b, c, signo FROM resultados WHERE fecha=? AND hora=?", (fecha_hoy, hora_etiqueta))
        return cursor.fetchone()

# --- LÓGICA DE TIEMPO VENEZUELA ---
ahora = datetime.now() - timedelta(hours=4)

# 1. Reloj de hora actual arriba
st.markdown(f"<div class='reloj-esquina'>{ahora.strftime('%I:%M:%S %p')}</div>", unsafe_allow_html=True)

# 2. Títulos
st.markdown("<div class='titulo-principal'>TRIPLE SAPO</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>DE SU LOTERÍA DE MARA</div>", unsafe_allow_html=True)

# 3. Contador Regresivo
horarios_metas = ["13:05:00", "17:05:00", "22:21:00"]
h_labels = ["01:05 PM", "05:05 PM", "10:21 PM"]

futuros = []
for h in horarios_metas:
    t = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if t < ahora: t += timedelta(days=1)
    futuros.append(t)

proximo = min(futuros)
restante = proximo - ahora
segundos_faltantes = int(restante.total_seconds())

horas, rem = divmod(segundos_faltantes, 3600)
minutos, segundos = divmod(rem, 60)
st.markdown(f"<div class='timer-grande'>{horas:02d}:{minutos:02d}:{segundos:02d}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaaaaa;'>PRÓXIMO SORTEO EN</p>", unsafe_allow_html=True)

# --- TABLERO DE RESULTADOS (CUADROS) ---
st.write("---")
cols = st.columns(3)
colores_borde = ["#ffcc00", "#00ffcc", "#ff3366"]

for i, h in enumerate(h_labels):
    with cols[i]:
        res = obtener_datos_hoy(h)
        
        # Iniciamos el HTML del cuadro con los resultados adentro
        contenido_cuadro = f"<h2 style='color: {colores_borde[i]}; margin-top: 0;'>{h}</h2>"
        
        if res:
            contenido_cuadro += f"""
                <p style='font-size: 20px; margin: 10px 0;'>A: {res[0]} | B: {res[1]} | C: {res[2]}</p>
                <h2 style='color: #ccff00; font-size: 30px; margin-bottom: 0;'>⭐ {res[3].upper()} ⭐</h2>
            """
        else:
            contenido_cuadro += "<p style='font-size: 18px; color: #888;'>Esperando...</p>"
            
        # Dibujamos el cuadro completo
        st.markdown(f"""
            <div class='card-sorteo' style='border: 4px solid {colores_borde[i]};'>
                {contenido_cuadro}
            </div>
        """, unsafe_allow_html=True)

# --- LÓGICA DE SORTEO AUTOMÁTICO ---
for idx, h_meta in enumerate(horarios_metas):
    t_sorteo = datetime.strptime(h_meta, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    label_actual = h_labels[idx]
    
    if ahora >= t_sorteo and not obtener_datos_hoy(label_actual):
        # Generar números
        r_a = "".join([str(random.randint(0, 9)) for _ in range(3)])
        r_b = "".join([str(random.randint(0, 9)) for _ in range(3)])
        r_c = "".join([str(random.randint(0, 9)) for _ in range(3)])
        signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        s_f = random.choice(signos)
        
        # Guardar
        fecha_str = ahora.strftime("%Y-%m-%d")
        with conectar_db() as db:
            db.execute("INSERT INTO resultados (fecha, hora, a, b, c, signo) VALUES (?,?,?,?,?,?)", 
                       (fecha_str, label_actual, r_a, r_b, r_c, s_f))
            db.commit()
        
        st.balloons()
        st.rerun()

st.sidebar.info("Lotería Triple Sapo - Mara, Venezuela")
