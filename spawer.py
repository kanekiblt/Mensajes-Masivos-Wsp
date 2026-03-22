import tkinter as tk
from tkinter import font as tkfont
import pyautogui as pg
import threading
import time

BG       = "#0a0a0a"
SURFACE  = "#111111"
ACCENT   = "#00ff88"
RED      = "#ff3c3c"
MUTED    = "#444444"
TEXT     = "#e0e0e0"

class Blaster(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLASTER")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._running = False
        self._thread  = None

        self._build_ui()

    def _build_ui(self):
        title_f = tkfont.Font(family="Courier New", size=36, weight="bold")
        sub_f   = tkfont.Font(family="Courier New", size=9)
        lbl_f   = tkfont.Font(family="Courier New", size=8)
        inp_f   = tkfont.Font(family="Courier New", size=12)
        btn_f   = tkfont.Font(family="Courier New", size=14, weight="bold")
        log_f   = tkfont.Font(family="Courier New", size=10)

        pad = 28

        tk.Label(self, text="BLASTER", font=title_f,
                 fg=ACCENT, bg=BG).place(x=pad, y=20)
        tk.Label(self, text="AUTO MESSAGE SENDER  ·  v2.0", font=sub_f,
                 fg=MUTED, bg=BG).place(x=pad+4, y=68)

        tk.Frame(self, bg=ACCENT, height=2, width=424).place(x=pad, y=90)

        y = 108

        tk.Label(self, text="MENSAJE", font=lbl_f,
                 fg=MUTED, bg=BG).place(x=pad, y=y)
        self.msj_var = tk.StringVar(value=" ")
        tk.Entry(self, textvariable=self.msj_var, font=inp_f,
                 bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=MUTED,
                 highlightcolor=ACCENT, width=36).place(x=pad, y=y+18)

        y += 60

        tk.Label(self, text="MENSAJES", font=lbl_f,
                 fg=MUTED, bg=BG).place(x=pad, y=y)
        self.num_var = tk.IntVar(value=10)
        tk.Spinbox(self, from_=1, to=9999, textvariable=self.num_var,
                   font=inp_f, bg=SURFACE, fg=ACCENT,
                   buttonbackground=SURFACE, relief="flat", bd=0,
                   highlightthickness=1, highlightbackground=MUTED,
                   highlightcolor=ACCENT, width=8,
                   insertbackground=ACCENT).place(x=pad, y=y+18)

        tk.Label(self, text="DELAY INICIAL (seg)", font=lbl_f,
                 fg=MUTED, bg=BG).place(x=200, y=y)
        self.delay_var = tk.DoubleVar(value=3.0)
        tk.Spinbox(self, from_=0, to=30, increment=0.5,
                   textvariable=self.delay_var,
                   font=inp_f, bg=SURFACE, fg=ACCENT,
                   buttonbackground=SURFACE, relief="flat", bd=0,
                   highlightthickness=1, highlightbackground=MUTED,
                   highlightcolor=ACCENT, width=8,
                   insertbackground=ACCENT).place(x=200, y=y+18)

        y += 62

        tk.Label(self, text="VELOCIDAD", font=lbl_f,
                 fg=MUTED, bg=BG).place(x=pad, y=y)
        self.interval_var = tk.IntVar(value=500)
        self.interval_lbl = tk.Label(self, text="500 ms", font=lbl_f,
                                     fg=ACCENT, bg=BG)
        self.interval_lbl.place(x=380, y=y)
        tk.Scale(self, from_=50, to=3000, resolution=50,
                 orient="horizontal", variable=self.interval_var,
                 bg=BG, fg=TEXT, troughcolor=SURFACE,
                 highlightthickness=0, relief="flat",
                 activebackground=ACCENT, sliderrelief="flat",
                 length=350, showvalue=False,
                 command=self._update_interval_label).place(x=pad, y=y+14)

        y += 60

        self.btn_start = tk.Button(self, text="INICIAR",
                                   font=btn_f, bg=ACCENT, fg=BG,
                                   relief="flat", bd=0, cursor="hand2",
                                   activebackground="#00cc6a",
                                   activeforeground=BG,
                                   command=self._start, width=12)
        self.btn_start.place(x=pad, y=y)

        self.btn_stop = tk.Button(self, text="DETENER",
                                  font=btn_f, bg=RED, fg=BG,
                                  relief="flat", bd=0, cursor="hand2",
                                  activebackground="#cc2020",
                                  activeforeground=BG,
                                  command=self._stop, width=12,
                                  state="disabled")
        self.btn_stop.place(x=200, y=y)

        y += 48

        self.status_var = tk.StringVar(value="Esperando...")
        tk.Label(self, textvariable=self.status_var, font=lbl_f,
                 fg=MUTED, bg=BG).place(x=pad, y=y)
        self.count_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.count_var, font=lbl_f,
                 fg=ACCENT, bg=BG).place(x=380, y=y)

        y += 18

        self.prog_canvas = tk.Canvas(self, width=424, height=3,
                                     bg=SURFACE, highlightthickness=0)
        self.prog_canvas.place(x=pad, y=y)
        self.prog_rect = self.prog_canvas.create_rectangle(
            0, 0, 0, 3, fill=ACCENT, outline="")

        y += 12

        self.log_box = tk.Text(self, font=log_f,
                               bg=SURFACE, fg=MUTED,
                               relief="flat", bd=0,
                               highlightthickness=1,
                               highlightbackground=MUTED,
                               state="disabled", width=54, height=8,
                               insertbackground=ACCENT)
        self.log_box.place(x=pad, y=y)
        self.log_box.tag_config("sent", foreground=ACCENT)
        self.log_box.tag_config("warn", foreground=RED)
        self.log_box.tag_config("info", foreground=TEXT)

        self._log("// Listo. Haz clic en INICIAR y cambia a la ventana destino.", "info")

    def _update_interval_label(self, val):
        self.interval_lbl.config(text=f"{val} ms")

    def _log(self, msg, tag="info"):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _set_progress(self, sent, total):
        pct = sent / total if total else 0
        self.prog_canvas.coords(self.prog_rect, 0, 0, int(424 * pct), 3)
        self.count_var.set(f"{sent} / {total}")

    def _start(self):
        msj      = self.msj_var.get()
        num      = self.num_var.get()
        delay    = self.delay_var.get()
        interval = self.interval_var.get() / 1000.0

        if not msj.strip():
            self._log("// [ERROR] El mensaje no puede estar vacío.", "warn")
            return

        self._running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self._set_progress(0, num)

        self._thread = threading.Thread(
            target=self._blast, args=(msj, num, delay, interval), daemon=True)
        self._thread.start()

    def _blast(self, msj, num, delay, interval):
        for i in range(int(delay), 0, -1):
            if not self._running:
                return
            self.status_var.set(f"Cambia a la ventana destino... {i}s")
            time.sleep(1)

        if not self._running:
            return

        self.status_var.set("Enviando mensajes...")
        self._log(f"// Enviando {num} mensaje(s) cada {int(interval*1000)}ms", "info")

        for i in range(1, num + 1):
            if not self._running:
                break
            pg.typewrite(msj, interval=0.02)
            pg.press('enter')
            self._log(f"[{str(i).zfill(4)}] {msj}", "sent")
            self.after(0, self._set_progress, i, num)
            time.sleep(interval)

        if self._running:
            self._done(i if self._running else i - 1)

    def _done(self, sent):
        self._running = False
        self.status_var.set(f"Completado. {sent} mensaje(s) enviados.")
        self._log(f"// [OK] Finalizado. {sent} mensajes enviados.", "info")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def _stop(self):
        self._running = False
        n = self.count_var.get().split("/")[0].strip()
        self.status_var.set(f"Detenido en mensaje {n}.")
        self._log(f"// [STOP] Detenido manualmente.", "warn")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")


if __name__ == "__main__":
    app = Blaster()
    app.mainloop()