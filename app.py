import random
import time
import sqlite3
from datetime import datetime
import schedule

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
def inicializar_db():
    try:
        with sqlite3.connect("sorteos_lotería.db") as conexion:
            cursor = conexion.cursor()
            # Añadimos columnas para Terminales para coincidir con la imagen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resultados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    hora_programada TEXT,
                    triple_a TEXT,
                    terminal_a TEXT,
                    triple_b TEXT,
                    terminal_b TEXT,
                    zodiacal TEXT
                )
            ''')
            conexion.commit()
    except sqlite3.Error as e:
        print(f"Error DB: {e}")

# --- LÓGICA DEL SORTEO ---
def ejecutar_sorteos_automaticos(hora_etiqueta):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generando sorteo...")
    
    # Función para generar Triple y extraer Terminal
    def generar_triple_y_terminal():
        num = random.randint(0, 999)
        triple = f"{num:03d}"
        terminal = triple[1:] # Toma los últimos 2 dígitos
        return triple, terminal

    # Generar resultados para A y B
    t_a, term_a = generar_triple_y_terminal()
    t_b, term_b = generar_triple_y_terminal()

    # Generar Zodiacal (Número de 3 dígitos + Signo)
    signos = ["ARIES", "TAURO", "GÉMINIS", "CÁNCER", "LEO", "VIRGO", 
              "LIBRA", "ESCORPIO", "SAGITARIO", "CAPRICORNIO", "ACUARIO", "PISCIS"]
    num_zodiacal = f"{random.randint(0, 999):03d}"
    res_zodiacal = f"{num_zodiacal} - {random.choice(signos)}"

    fecha_hoy = datetime.now().strftime("%d/%m/%Y") # Formato DD/MM/YYYY como la imagen
    
    try:
        with sqlite3.connect("sorteos_lotería.db") as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO resultados (fecha, hora_programada, triple_a, terminal_a, triple_b, terminal_b, zodiacal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_hoy, hora_etiqueta, t_a, term_a, t_b, term_b, res_zodiacal))
            conexion.commit()
        
        print(f"✅ SORTEO REALIZADO ({hora_etiqueta})")
        print(f"A: {t_a} ({term_a}) | B: {t_b} ({term_b}) | Zod: {res_zodiacal}")
    except sqlite3.Error as e:
        print(f"❌ Error al guardar: {e}")

# --- PROGRAMACIÓN ---
inicializar_db()

# Horarios ajustados a los de la imagen (ejemplos)
schedule.every().day.at("11:45").do(ejecutar_sorteos_automaticos, hora_etiqueta="11:45 am")
schedule.every().day.at("15:45").do(ejecutar_sorteos_automaticos, hora_etiqueta="03:45 pm")
schedule.every().day.at("21:45").do(ejecutar_sorteos_automaticos, hora_etiqueta="09:45 pm")

print("Servidor de Lotería iniciado. Esperando la hora del sorteo...")

while True:
    schedule.run_pending()
    time.sleep(1)
