"""
Gestor Unificado de Mensajes Masivos
=====================================
Soporta: WhatsApp (pywhatkit), Instagram (selenium), SMS (pyautogui)

Instalación de dependencias:
    pip install pywhatkit selenium pyautogui webdriver-manager pillow
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re


# ─────────────────────────────────────────────
#  BACKEND — lógica de envío por plataforma
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  HELPER — inicializa el navegador Brave
# ─────────────────────────────────────────────

def _crear_driver(log_fn):
    """
    Crea un WebDriver usando Chrome con webdriver-manager.
    Descarga automáticamente el ChromeDriver que coincide con tu versión de Chrome.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    log_fn("🚀 Chrome listo.")
    return driver


def enviar_whatsapp(numero: str, mensaje: str, cantidad: int, log_fn, delay: int = 3):
    """
    Abre WhatsApp Web UNA sola vez y envía todos los mensajes consecutivamente.
    El navegador permanece abierto durante todo el proceso.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
    except ImportError:
        log_fn("❌ Instala dependencias: pip install selenium webdriver-manager")
        return

    if not numero.startswith("+"):
        numero = "+" + numero

    log_fn("🌐 Abriendo WhatsApp Web en Chrome... escanea el QR si es necesario.")

    try:
        driver = _crear_driver(log_fn)
        driver.get(f"https://web.whatsapp.com/send?phone={numero}")
        log_fn("⏳ Tienes 20 segundos para escanear el QR si es necesario...")
        time.sleep(20)

        wait = WebDriverWait(driver, 20)

        for i in range(1, cantidad + 1):
            try:
                caja = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@title="Type a message" or @title="Escribe un mensaje"]')
                ))
                caja.click()
                caja.send_keys(mensaje)
                caja.send_keys(Keys.RETURN)
                log_fn(f"✅ WhatsApp [{i}/{cantidad}] enviado a {numero}")
                time.sleep(delay)
            except Exception as e:
                log_fn(f"❌ Error en mensaje {i}: {e}")
                break

        time.sleep(2)
        driver.quit()
    except Exception as e:
        log_fn(f"❌ Error al iniciar el navegador: {e}")


def enviar_instagram(username: str, mensaje: str, cantidad: int, log_fn, delay: int = 3):
    """
    Abre Instagram UNA sola vez y envía todos los mensajes consecutivamente.
    El navegador permanece abierto durante todo el proceso.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
    except ImportError:
        log_fn("❌ Instala dependencias: pip install selenium webdriver-manager")
        return

    log_fn("🌐 Abriendo Instagram en Chrome... inicia sesión si es necesario.")

    try:
        driver = _crear_driver(log_fn)
        driver.get("https://www.instagram.com/direct/t/" + username.lstrip("@"))
        log_fn("⏳ Tienes 20 segundos para iniciar sesión si es necesario...")
        time.sleep(20)

        wait = WebDriverWait(driver, 15)

        for i in range(1, cantidad + 1):
            try:
                caja = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@aria-label="Mensaje" or @aria-label="Message"]')
                ))
                caja.click()
                caja.send_keys(mensaje)
                caja.send_keys(Keys.RETURN)
                log_fn(f"✅ Instagram [{i}/{cantidad}] enviado a @{username}")
                time.sleep(delay)
            except Exception as e:
                log_fn(f"❌ Error en mensaje {i}: {e}")
                break

        time.sleep(2)
        driver.quit()
    except Exception as e:
        log_fn(f"❌ Error al iniciar el navegador: {e}")


def enviar_sms(cantidad: int, mensaje: str, log_fn):
    """
    Envía SMS usando pyautogui.
    El usuario debe abrir la app de mensajes manualmente.
    """
    try:
        import pyautogui
    except ImportError:
        log_fn("❌ Instala pyautogui: pip install pyautogui")
        return

    log_fn("⏳ Tienes 5 segundos para abrir la app de mensajes y colocarte en el campo de texto...")
    for i in range(5, 0, -1):
        log_fn(f"   Comenzando en {i}...")
        time.sleep(1)

    for i in range(1, cantidad + 1):
        try:
            pyautogui.typewrite(mensaje, interval=0.05)
            pyautogui.press("enter")
            log_fn(f"✅ SMS [{i}/{cantidad}] enviado")
            time.sleep(2)
        except Exception as e:
            log_fn(f"❌ Error en mensaje {i}: {e}")


# ─────────────────────────────────────────────
#  GUI — Interfaz gráfica con tkinter
# ─────────────────────────────────────────────

COLORES = {
    "fondo": "#0f0f0f",
    "panel": "#1a1a1a",
    "borde": "#2a2a2a",
    "acento": "#25D366",       # Verde WhatsApp como color principal
    "acento2": "#E1306C",      # Rosa Instagram
    "acento3": "#00AAFF",      # Azul SMS
    "texto": "#f0f0f0",
    "texto_dim": "#888888",
    "entrada": "#222222",
}

PLATAFORMAS = {
    "WhatsApp": {"color": "#25D366", "icono": "💬", "campo": "Número (ej: 51999888777)"},
    "Instagram": {"color": "#E1306C", "icono": "📸", "campo": "Usuario (ej: @usuario)"},
    "SMS":       {"color": "#00AAFF", "icono": "📱", "campo": "Abre la app manualmente"},
}


class GestorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestor de Mensajes Masivos")
        self.root.geometry("680x720")
        self.root.configure(bg=COLORES["fondo"])
        self.root.resizable(False, False)

        self.plataforma_var = tk.StringVar(value="WhatsApp")
        self.enviando = False

        self._construir_ui()

    # ── Construcción de la UI ──────────────────

    def _construir_ui(self):
        # Título
        titulo_frame = tk.Frame(self.root, bg=COLORES["fondo"])
        titulo_frame.pack(pady=(28, 8), padx=30, fill="x")

        tk.Label(
            titulo_frame,
            text="GESTOR DE MENSAJES",
            font=("Courier New", 20, "bold"),
            bg=COLORES["fondo"],
            fg=COLORES["texto"],
        ).pack(side="left")

        tk.Label(
            titulo_frame,
            text=" MASIVOS",
            font=("Courier New", 20, "bold"),
            bg=COLORES["fondo"],
            fg=COLORES["acento"],
        ).pack(side="left")

        # Selector de plataforma
        self._seccion("PLATAFORMA")
        plat_frame = tk.Frame(self.root, bg=COLORES["fondo"])
        plat_frame.pack(padx=30, fill="x", pady=(4, 12))

        self.botones_plat = {}
        for nombre, info in PLATAFORMAS.items():
            btn = tk.Button(
                plat_frame,
                text=f"{info['icono']}  {nombre}",
                font=("Courier New", 11, "bold"),
                bg=COLORES["panel"],
                fg=COLORES["texto_dim"],
                relief="flat",
                cursor="hand2",
                padx=16, pady=10,
                command=lambda n=nombre: self._seleccionar_plataforma(n),
            )
            btn.pack(side="left", padx=(0, 10))
            self.botones_plat[nombre] = btn

        # Destino
        self._seccion("DESTINO")
        self.lbl_destino = tk.Label(
            self.root,
            text="Número (ej: 51999888777)",
            font=("Courier New", 9),
            bg=COLORES["fondo"],
            fg=COLORES["texto_dim"],
        )
        self.lbl_destino.pack(padx=30, anchor="w", pady=(2, 4))

        self.entrada_destino = tk.Entry(
            self.root,
            font=("Courier New", 13),
            bg=COLORES["entrada"],
            fg=COLORES["texto"],
            insertbackground=COLORES["texto"],
            relief="flat",
            bd=0,
        )
        self.entrada_destino.pack(padx=30, fill="x", ipady=10)
        self._borde(self.entrada_destino)

        # Mensaje
        self._seccion("MENSAJE")
        self.entrada_mensaje = scrolledtext.ScrolledText(
            self.root,
            font=("Courier New", 12),
            bg=COLORES["entrada"],
            fg=COLORES["texto"],
            insertbackground=COLORES["texto"],
            relief="flat",
            bd=0,
            height=5,
            wrap="word",
        )
        self.entrada_mensaje.pack(padx=30, fill="x")
        self._borde(self.entrada_mensaje)

        # Cantidad
        self._seccion("CANTIDAD DE MENSAJES")
        cant_frame = tk.Frame(self.root, bg=COLORES["fondo"])
        cant_frame.pack(padx=30, fill="x", pady=(4, 0))

        self.slider_cant = tk.Scale(
            cant_frame,
            from_=1, to=50,
            orient="horizontal",
            bg=COLORES["fondo"],
            fg=COLORES["texto"],
            troughcolor=COLORES["panel"],
            activebackground=COLORES["acento"],
            highlightthickness=0,
            font=("Courier New", 10),
            length=460,
            showvalue=False,
            command=self._actualizar_label_cant,
        )
        self.slider_cant.set(5)
        self.slider_cant.pack(side="left")

        self.lbl_cant = tk.Label(
            cant_frame,
            text="5",
            font=("Courier New", 18, "bold"),
            bg=COLORES["fondo"],
            fg=COLORES["acento"],
            width=4,
        )
        self.lbl_cant.pack(side="left", padx=(12, 0))

        # Delay entre mensajes
        self._seccion("DELAY ENTRE MENSAJES")
        delay_frame = tk.Frame(self.root, bg=COLORES["fondo"])
        delay_frame.pack(padx=30, fill="x", pady=(4, 0))

        self.slider_delay = tk.Scale(
            delay_frame,
            from_=1, to=10,
            orient="horizontal",
            bg=COLORES["fondo"],
            fg=COLORES["texto"],
            troughcolor=COLORES["panel"],
            activebackground=COLORES["acento"],
            highlightthickness=0,
            font=("Courier New", 10),
            length=460,
            showvalue=False,
            command=self._actualizar_label_delay,
        )
        self.slider_delay.set(3)
        self.slider_delay.pack(side="left")

        self.lbl_delay = tk.Label(
            delay_frame,
            text="3s",
            font=("Courier New", 18, "bold"),
            bg=COLORES["fondo"],
            fg=COLORES["acento"],
            width=4,
        )
        self.lbl_delay.pack(side="left", padx=(12, 0))

        # Botón de enviar
        self.btn_enviar = tk.Button(
            self.root,
            text="▶  INICIAR ENVÍO",
            font=("Courier New", 13, "bold"),
            bg=COLORES["acento"],
            fg="#000000",
            relief="flat",
            cursor="hand2",
            padx=20, pady=14,
            command=self._iniciar_envio,
        )
        self.btn_enviar.pack(padx=30, fill="x", pady=(20, 8))

        # Log
        self._seccion("REGISTRO")
        self.log_box = scrolledtext.ScrolledText(
            self.root,
            font=("Courier New", 10),
            bg=COLORES["panel"],
            fg=COLORES["acento"],
            insertbackground=COLORES["texto"],
            relief="flat",
            bd=0,
            height=6,
            state="disabled",
        )
        self.log_box.pack(padx=30, fill="x", pady=(4, 20))

        # Selección inicial — AL FINAL cuando todos los widgets ya existen
        self._seleccionar_plataforma("WhatsApp")

    def _seccion(self, texto: str):
        frame = tk.Frame(self.root, bg=COLORES["fondo"])
        frame.pack(padx=30, fill="x", pady=(14, 0))
        tk.Label(
            frame,
            text=texto,
            font=("Courier New", 8, "bold"),
            bg=COLORES["fondo"],
            fg=COLORES["texto_dim"],
        ).pack(side="left")
        tk.Frame(frame, bg=COLORES["borde"], height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=6
        )

    def _borde(self, widget):
        """Añade un frame de borde debajo del widget."""
        tk.Frame(self.root, bg=COLORES["borde"], height=1).pack(padx=30, fill="x")

    # ── Lógica de interacción ──────────────────

    def _seleccionar_plataforma(self, nombre: str):
        self.plataforma_var.set(nombre)
        color = PLATAFORMAS[nombre]["color"]
        campo = PLATAFORMAS[nombre]["campo"]

        for n, btn in self.botones_plat.items():
            if n == nombre:
                btn.config(bg=color, fg="#000000")
            else:
                btn.config(bg=COLORES["panel"], fg=COLORES["texto_dim"])

        self.lbl_destino.config(text=campo)
        self.btn_enviar.config(bg=color)

        # Deshabilitar campo destino para SMS (no se necesita)
        if nombre == "SMS":
            self.entrada_destino.config(state="disabled", fg=COLORES["texto_dim"])
        else:
            self.entrada_destino.config(state="normal", fg=COLORES["texto"])

    def _actualizar_label_cant(self, valor):
        self.lbl_cant.config(text=str(valor))

    def _actualizar_label_delay(self, valor):
        self.lbl_delay.config(text=f"{valor}s")

    def _log(self, mensaje: str):
        self.log_box.config(state="normal")
        self.log_box.insert("end", mensaje + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _iniciar_envio(self):
        if self.enviando:
            return

        plataforma = self.plataforma_var.get()
        destino = self.entrada_destino.get().strip()
        mensaje = self.entrada_mensaje.get("1.0", "end").strip()
        cantidad = int(self.slider_cant.get())

        # Validaciones
        if not mensaje:
            messagebox.showwarning("Campo vacío", "Escribe un mensaje antes de enviar.")
            return

        if plataforma != "SMS" and not destino:
            messagebox.showwarning("Campo vacío", f"Ingresa el {PLATAFORMAS[plataforma]['campo'].lower()}.")
            return

        self.enviando = True
        self.btn_enviar.config(text="⏳  ENVIANDO...", state="disabled")
        self._log(f"\n{'─'*40}")
        self._log(f"🚀 Iniciando: {plataforma} | Cantidad: {cantidad}")

        delay = int(self.slider_delay.get())

        def tarea():
            try:
                if plataforma == "WhatsApp":
                    enviar_whatsapp(destino, mensaje, cantidad, self._log, delay)
                elif plataforma == "Instagram":
                    enviar_instagram(destino, mensaje, cantidad, self._log, delay)
                elif plataforma == "SMS":
                    enviar_sms(cantidad, mensaje, self._log)
            finally:
                self.enviando = False
                color = PLATAFORMAS[plataforma]["color"]
                self.root.after(0, lambda: self.btn_enviar.config(
                    text="▶  INICIAR ENVÍO", state="normal", bg=color
                ))
                self._log("✔ Proceso finalizado.")

        threading.Thread(target=tarea, daemon=True).start()


# ─────────────────────────────────────────────
#  ENTRADA PRINCIPAL
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = GestorApp(root)
    root.mainloop()