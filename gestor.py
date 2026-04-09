import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import threading
import requests
import pandas as pd
import datetime
import time
import csv

# ─────────────────────────────
# CONFIG API (RELLENA ESTO)
# ─────────────────────────────
PHONE_NUMBER_ID = "TU_PHONE_NUMBER_ID"
ACCESS_TOKEN = "TU_ACCESS_TOKEN"

# ─────────────────────────────
# TEMA OSCURO PRO
# ─────────────────────────────
BG = "#0d1117"
PANEL = "#161b22"
ACCENT = "#238636"
TEXT = "#e6edf3"
MUTED = "#8b949e"

# ─────────────────────────────
# API WHATSAPP CLOUD
# ─────────────────────────────
def enviar_whatsapp_api(numero, mensaje):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    return r.status_code, r.text

# ─────────────────────────────
# AUTO RESPUESTA INTELIGENTE
# ─────────────────────────────
REGLAS = {
    "precio": "💰 Nuestro precio actual es S/49. ¿Te envío el link de pago?",
    "horario": "🕒 Atendemos de 9am a 6pm.",
    "ubicacion": "📍 Estamos en el centro. ¿Quieres el mapa?"
}

def auto_responder(texto_entrante):
    t = texto_entrante.lower()
    for clave, resp in REGLAS.items():
        if clave in t:
            return resp
    return None

# ─────────────────────────────
# PROGRAMADOR
# ─────────────────────────────
def programar_envio(fecha, hora, funcion):
    objetivo = datetime.datetime.combine(fecha, hora)
    while True:
        if datetime.datetime.now() >= objetivo:
            funcion()
            break
        time.sleep(1)

# ─────────────────────────────
# REPORTE CSV
# ─────────────────────────────
def guardar_reporte(filas):
    nombre = f"reporte_envios_{int(time.time())}.csv"
    with open(nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["numero", "estado", "respuesta"])
        w.writerows(filas)
    return nombre

# ─────────────────────────────
# UI
# ─────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        root.title("Gestor Mensajes PRO")
        root.geometry("620x720")
        root.configure(bg=BG)
        root.resizable(False, False)

        self.excel = None
        self._ui()

    def _ui(self):
        tk.Label(self.root, text="GESTOR PRO", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(pady=20)

        self._seccion("Lista de contactos (Excel)")
        tk.Button(self.root, text="Cargar Excel",
                  command=self.cargar_excel).pack(padx=30, fill="x")

        self._seccion("Mensaje")
        self.msg = tk.Text(self.root, height=5, bg=PANEL, fg=TEXT)
        self.msg.pack(padx=30, fill="x")

        self._seccion("Programar envío")
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(padx=30, fill="x")
        self.fecha = DateEntry(frame)
        self.fecha.pack(side="left", expand=True, fill="x")
        self.hora = ttk.Combobox(frame, values=[f"{h:02d}:00" for h in range(24)])
        self.hora.set("12:00")
        self.hora.pack(side="left", expand=True, fill="x", padx=10)

        tk.Button(self.root, text="Programar Envío",
                  bg=ACCENT, fg="white",
                  command=self.programar).pack(padx=30, fill="x", pady=20)

        self.log = tk.Text(self.root, height=10, bg=PANEL, fg=ACCENT)
        self.log.pack(padx=30, fill="x")

    def _seccion(self, t):
        tk.Label(self.root, text=t, bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(padx=30, anchor="w", pady=(15,5))

    def cargar_excel(self):
        ruta = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if ruta:
            self.excel = ruta
            self._log(f"Excel cargado: {ruta}")

    def _log(self, t):
        self.log.insert("end", t + "\n")
        self.log.see("end")

    def programar(self):
        if not self.excel:
            messagebox.showwarning("Falta Excel", "Carga un Excel primero")
            return

        mensaje = self.msg.get("1.0", "end").strip()
        if not mensaje:
            messagebox.showwarning("Mensaje vacío", "Escribe un mensaje")
            return

        fecha = self.fecha.get_date()
        h, m = map(int, self.hora.get().split(":"))
        hora = datetime.time(hour=h, minute=m)

        def tarea():
            self._log("Envío iniciado...")
            df = pd.read_excel(self.excel)
            reporte = []

            for num in df.iloc[:,0].dropna():
                estado, resp = enviar_whatsapp_api(str(num), mensaje)
                ok = "OK" if estado == 200 else "ERROR"
                reporte.append([num, ok, resp])
                self._log(f"{num} → {ok}")

            archivo = guardar_reporte(reporte)
            self._log(f"Reporte guardado: {archivo}")

        threading.Thread(
            target=programar_envio,
            args=(fecha, hora, tarea),
            daemon=True
        ).start()

        self._log("Envío programado.")

# ─────────────────────────────
# MAIN
# ─────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()