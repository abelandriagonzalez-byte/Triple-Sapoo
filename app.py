import random
import time
import sqlite3
import tkinter as tk
from tkinter import PhotoImage
from datetime import datetime, timedelta
import threading
import schedule

# --- MANEJO DE AUDIO (A PRUEBA DE ERRORES) ---
try:
    import pygame
    pygame.mixer.init()
    PYGAME_INSTALADO = True
except ImportError:
    PYGAME_INSTALADO = False

def reproducir_sonido(archivo, loops=0):
    if PYGAME_INSTALADO:
        try:
            pygame.mixer.music.load(archivo)
            pygame.mixer.music.play(loops)
        except:
            pass

def detener_sonido():
    if PYGAME_INSTALADO:
        try:
            pygame.mixer.music.stop()
        except:
            pass

# --- BASE DE DATOS ---
def obtener_datos(hora, dias_atras=0):
    try:
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        with sqlite3.connect("sorteos_lotería.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sorteo_a, sorteo_b, sorteo_c, zodiacal FROM resultados WHERE fecha=? AND hora_programada=?", (fecha, hora))
            res = cursor.fetchone()
            if res:
                return f"A: {res[0]}\nB: {res[1]}\nC: {res[2]}\n⭐ {res[3].upper()} ⭐"
        return "Esperando..."
    except:
        return "---"

# --- TÓMBOLA EN VIVO ---
class TombolaVivo(tk.Toplevel):
    def __init__(self, parent, hora_etiqueta, callback_actualizar):
        super().__init__(parent)
        self.callback_actualizar = callback_actualizar
        self.title("¡SORTEO EN VIVO!")
        self.attributes("-fullscreen", True)
        self.configure(bg="#051a05")
        self.attributes("-topmost", True)
        self.hora_etiqueta = hora_etiqueta
        
        tk.Label(self, text="SORTEO EN VIVO", font=("Arial Black", 40), bg="#051a05", fg="#ccff00").pack(pady=40)
        self.canvas = tk.Canvas(self, width=800, height=300, bg="#051a05", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        self.bolas_ui = []
        for i in range(3):
            self.canvas.create_oval(50 + (i*250), 20, 230 + (i*250), 200, fill="#ffffff", outline="#ccff00", width=5)
            txt = self.canvas.create_text(140 + (i*250), 110, text="?", font=("Arial Black", 80), fill="#1a3c1a")
            self.bolas_ui.append(txt)
            
        self.lbl_tipo = tk.Label(self, text="¡MUCHA SUERTE!", font=("Arial Black", 30), bg="#051a05", fg="#ffff00")
        self.lbl_tipo.pack(pady=40)
        
        threading.Thread(target=self.iniciar_sorteo, daemon=True).start()

    def iniciar_sorteo(self):
        signos = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        res_a, res_b, res_c = ["".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(3)]
        signo_final = random.choice(signos)
        
        datos_finales = [res_a, res_b, res_c]
        tipos = ["TRIPLE A", "TRIPLE B", "TRIPLE C"]

        for idx, t in enumerate(tipos):
            self.lbl_tipo.config(text=f"SORTEANDO: {t}")
            reproducir_sonido("giro.mp3", loops=-1)
            for _ in range(15):
                for b_idx in range(3):
                    self.canvas.itemconfig(self.bolas_ui[b_idx], text=str(random.randint(0, 9)))
                time.sleep(0.08)
            detener_sonido()
            
            val_final = datos_finales[idx]
            for i, num in enumerate(val_final):
                self.canvas.itemconfig(self.bolas_ui[i], text=num)
                reproducir_sonido("bola.mp3")
                time.sleep(0.5)
            time.sleep(1.5)

        self.lbl_tipo.config(text="SORTEANDO SIGNO...")
        reproducir_sonido("giro.mp3", loops=-1)
        for _ in range(20):
            sz = random.choice(signos)
            self.lbl_tipo.config(text=f"SIGNO: {sz.upper()}")
            time.sleep(0.1)
        detener_sonido()
        
        self.lbl_tipo.config(text=f"GANADOR: {signo_final.upper()}", fg="#ccff00")
        reproducir_sonido("exito.mp3")

        with sqlite3.connect("sorteos_lotería.db") as conn:
            conn.execute("INSERT INTO resultados (fecha, hora_programada, sorteo_a, sorteo_b, sorteo_c, zodiacal) VALUES (?,?,?,?,?,?)", 
                         (datetime.now().strftime("%Y-%m-%d"), self.hora_etiqueta, res_a, res_b, res_c, signo_final))
        
        time.sleep(5)
        self.after(0, self.finalizar)

    def finalizar(self):
        self.callback_actualizar()
        self.destroy()

# --- INTERFAZ PRINCIPAL ---
class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Oficial - Triple Sapo")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#1a3c1a")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.frame_header = tk.Frame(root, bg="#1a3c1a")
        self.frame_header.pack(pady=40, fill="x")
        
        tk.Label(self.frame_header, text="TRIPLE SAPO", font=("Arial Black", 50), bg="#1a3c1a", fg="#ccff00").pack()
        
        self.lbl_timer = tk.Label(root, text="00:00:00", font=("Consolas", 90, "bold"), bg="#1a3c1a", fg="white")
        self.lbl_timer.pack(pady=20)

        self.cuadros_hoy = {}
        # RESTAURADO: Horario de 09:05 PM
        self.horarios = [("01:05 PM", "#ffcc00"), ("05:05 PM", "#00ffcc"), ("09:05 PM", "#ff3366")]
        
        f_hoy = tk.Frame(root, bg="#1a3c1a")
        f_hoy.pack(pady=20)

        for h, c in self.horarios:
            f = tk.Frame(f_hoy, bg="#2d5a27", highlightbackground=c, highlightthickness=4, width=350, height=280)
            f.pack_propagate(False)
            f.pack(side="left", padx=20)
            tk.Label(f, text=h, font=("Arial", 20, "bold"), bg="#2d5a27", fg=c).pack(pady=15)
            lbl = tk.Label(f, text="Cargando...", font=("Arial", 22, "bold"), bg="#2d5a27", fg="white", justify="center")
            lbl.pack(expand=True)
            self.cuadros_hoy[h] = lbl

        self.actualizar_todo()

    def actualizar_todo(self):
        # RESTAURADO: 21:05:00
        metas = ["13:05:00", "17:05:00", "21:05:00"]
        ahora = datetime.now()
        futuros = []
        for h in metas:
            f = datetime.strptime(h, "%H:%M:%S").replace(year=ahora.year, month=ahora.month, day=ahora.day)
            if f <= ahora:
                f += timedelta(days=1)
            futuros.append(f)
        
        diff = min(futuros) - ahora
        s = int(diff.total_seconds())
        self.lbl_timer.config(text=f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}")

        for h in self.cuadros_hoy:
            self.cuadros_hoy[h].config(text=obtener_datos(h))
            
        self.root.after(1000, self.actualizar_todo)

    def lanzar_tombola(self, hora):
        TombolaVivo(self.root, hora, self.actualizar_todo)

def scheduler_loop(app_instance, root_ref):
    schedule.every().day.at("13:05").do(lambda: root_ref.after(0, app_instance.lanzar_tombola, "01:05 PM"))
    schedule.every().day.at("17:05").do(lambda: root_ref.after(0, app_instance.lanzar_tombola, "05:05 PM"))
    # RESTAURADO: Programación a las 21:05
    schedule.every().day.at("21:05").do(lambda: root_ref.after(0, app_instance.lanzar_tombola, "09:05 PM"))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    with sqlite3.connect("sorteos_lotería.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, 
                        hora_programada TEXT, sorteo_a TEXT, sorteo_b TEXT, 
                        sorteo_c TEXT, zodiacal TEXT)''')

    root = tk.Tk()
    app = AppPrincipal(root)
    threading.Thread(target=scheduler_loop, args=(app, root), daemon=True).start()
    root.mainloop()
