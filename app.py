import random
import time
import sqlite3
import tkinter as tk
from tkinter import PhotoImage
from datetime import datetime, timedelta
import threading
import schedule
import pygame

# --- AUDIO ---
pygame.mixer.init()

def reproducir_sonido(archivo, loops=0):
    try:
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.play(loops)
    except: pass

def detener_sonido():
    pygame.mixer.music.stop()

# --- BASE DE DATOS ---
def inicializar_db():
    with sqlite3.connect("sorteos_lotería.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hora_programada TEXT, 
                        sorteo_a TEXT, sorteo_b TEXT, sorteo_c TEXT, zodiacal TEXT)''')

def obtener_datos(hora, dias_atras=0):
    try:
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        with sqlite3.connect("sorteos_lotería.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sorteo_a, sorteo_b, sorteo_c, zodiacal FROM resultados WHERE fecha=? AND hora_programada=?", (fecha, hora))
            res = cursor.fetchone()
            if res:
                return f"A: {res[0]}\nB: {res[1]}\nC: {res[2]}\n⭐ {res[3].upper()} ⭐"
            return "Esperando..." if dias_atras == 0 else "---"
    except: return "---"

# --- INTERFAZ TÓMBOLA ---
class TombolaVivo(tk.Toplevel):
    def __init__(self, parent, hora_etiqueta, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.attributes("-fullscreen", True)
        self.configure(bg="#051a05")
        self.attributes("-topmost", True)
        self.hora_etiqueta = hora_etiqueta
        
        tk.Label(self, text="SORTEO EN VIVO", font=("Arial Black", 45), bg="#051a05", fg="#ccff00").pack(pady=40)
        self.canvas = tk.Canvas(self, width=900, height=300, bg="#051a05", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.bolas_ui = []
        for i in range(3):
            self.canvas.create_oval(50 + (i*280), 20, 250 + (i*280), 220, fill="#ffffff", outline="#ccff00", width=6)
            txt = self.canvas.create_text(150 + (i*280), 120, text="?", font=("Arial Black", 90), fill="#1a3c1a")
            self.bolas_ui.append(txt)
        self.lbl_tipo = tk.Label(self, text="¡SUERTE!", font=("Arial Black", 35), bg="#051a05", fg="#ffff00")
        self.lbl_tipo.pack(pady=50)
        threading.Thread(target=self.iniciar_sorteo, daemon=True).start()

    def iniciar_sorteo(self):
        signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        res_a, res_b, res_c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        s_f = random.choice(signos)
        datos = [res_a, res_b, res_c]
        for idx, t in enumerate(["TRIPLE A", "TRIPLE B", "TRIPLE C"]):
            self.lbl_tipo.config(text=f"SORTEANDO: {t}")
            reproducir_sonido("giro.mp3", loops=-1)
            for _ in range(15):
                for b_idx in range(3): self.canvas.itemconfig(self.bolas_ui[b_idx], text=str(random.randint(0, 9)))
                time.sleep(0.08)
            detener_sonido()
            for i, num in enumerate(datos[idx]):
                self.canvas.itemconfig(self.bolas_ui[i], text=num)
                reproducir_sonido("bola.mp3"); time.sleep(0.6)
            time.sleep(1.5)
        self.lbl_tipo.config(text="SORTEANDO SIGNO...")
        reproducir_sonido("giro.mp3", loops=-1)
        for _ in range(20):
            self.lbl_tipo.config(text=f"SIGNO: {random.choice(signos).upper()}"); time.sleep(0.1)
        detener_sonido()
        self.lbl_tipo.config(text=f"GANADOR: {s_f.upper()}", fg="#ccff00"); reproducir_sonido("exito.mp3")
        with sqlite3.connect("sorteos_lotería.db") as conn:
            conn.execute("INSERT INTO resultados (fecha, hora_programada, sorteo_a, sorteo_b, sorteo_c, zodiacal) VALUES (?,?,?,?,?,?)",
                         (datetime.now().strftime("%Y-%m-%d"), self.hora_etiqueta, res_a, res_b, res_c, s_f))
        time.sleep(5); self.callback_actualizar(); self.destroy()

# --- INTERFAZ PRINCIPAL ---
class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Triple Sapo - Monitor")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#1a3c1a")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # --- RELOJ SIMPLE (Sin marcos, solo texto) ---
        # x=-150 para que esté bien adentro de la pantalla
        self.lbl_reloj_simple = tk.Label(root, text="00:00:00 AM", font=("Arial", 30, "bold"), bg="#1a3c1a", fg="white")
        self.lbl_reloj_simple.place(relx=1.0, x=-150, y=40, anchor="ne")

        # Cabecera
        self.frame_header = tk.Frame(root, bg="#1a3c1a")
        self.frame_header.pack(pady=40, fill="x")
        try:
            self.img_logo = PhotoImage(file="logo.png").subsample(2, 2)
            tk.Label(self.frame_header, image=self.img_logo, bg="#1a3c1a").pack(side="left", padx=60)
            tk.Label(self.frame_header, image=self.img_logo, bg="#1a3c1a").pack(side="right", padx=60)
        except: pass

        self.frame_titulo = tk.Frame(self.frame_header, bg="#1a3c1a")
        self.frame_titulo.pack(expand=True)
        tk.Label(self.frame_titulo, text="TRIPLE SAPO", font=("Arial Black", 55, "bold"), bg="#1a3c1a", fg="#ccff00").pack()
        tk.Label(self.frame_titulo, text="DE SU LOTERÍA DE MARA", font=("Arial", 22, "italic", "bold"), bg="#1a3c1a", fg="#ffff00").pack()

        self.lbl_timer = tk.Label(root, text="00:00:00", font=("Consolas", 100, "bold"), bg="#1a3c1a", fg="white")
        self.lbl_timer.pack(pady=20)

        # Resultados
        self.cuadros_hoy = {}
        self.horarios = [("01:05 PM", "#ffcc00"), ("05:05 PM", "#00ffcc"), ("09:05 PM", "#ff3366")]
        f_hoy = tk.Frame(root, bg="#1a3c1a"); f_hoy.pack(pady=30)
        for h, c in self.horarios:
            f = tk.Frame(f_hoy, bg="#2d5a27", highlightbackground=c, highlightthickness=5, width=360, height=300)
            f.pack_propagate(False); f.pack(side="left", padx=20)
            tk.Label(f, text=h, font=("Arial", 20, "bold"), bg="#2d5a27", fg=c).pack(pady=15)
            lbl = tk.Label(f, text="Esperando...", font=("Arial", 22, "bold"), bg="#2d5a27", fg="white")
            lbl.pack(expand=True); self.cuadros_hoy[h] = lbl

        self.actualizar()

    def actualizar(self):
        ahora = datetime.now()
        # Actualización del reloj simple
        self.lbl_reloj_simple.config(text=ahora.strftime("%I:%M:%S %p"))
        
        metas = ["13:05:00", "17:05:00", "21:05:00"]
        futuros = [datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in metas]
        futuros = [f if f > ahora else f + timedelta(days=1) for f in futuros]
        diff = min(futuros) - ahora
        s = int(diff.total_seconds())
        self.lbl_timer.config(text=f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}")
        
        for h in self.cuadros_hoy: self.cuadros_hoy[h].config(text=obtener_datos(h, 0))
        self.root.after(1000, self.actualizar)

def lanzar(hora): TombolaVivo(root, hora, app.actualizar)

def loop():
    schedule.every().day.at("13:05").do(lanzar, hora="01:05 PM")
    schedule.every().day.at("17:05").do(lanzar, hora="05:05 PM")
    schedule.every().day.at("21:05").do(lanzar, hora="09:05 PM")
    while True: schedule.run_pending(); time.sleep(1)

if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk(); app = AppPrincipal(root)
    threading.Thread(target=loop, daemon=True).start()
    root.mainloop()
