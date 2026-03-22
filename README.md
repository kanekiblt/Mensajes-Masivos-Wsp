# 📨 Mensajes-Masivos-Wsp — WhatsApp Mass Messenger

A simple Python tool that lets you send repeated messages automatically to any WhatsApp contact using keyboard automation.

---

## 🚀 How It Works

The tool uses `pyautogui` to simulate keystrokes on your screen. You choose how many messages to send, switch to the WhatsApp chat window, and the script handles the rest.

---

## 📦 Installation

Make sure you have Python installed, then run:

```bash
pip install pyautogui
```

---

## 🗂️ Project Files

| File | Description |
|------|-------------|
| `spawer.py` | **v1** — Console-based version. Runs entirely in the terminal. |
| `wsp.py` | **v2** — Improved version with a GUI built using `tkinter` for a better experience. |
| `spammer.html` | A visual mockup showing how the tool could look as a web application. |

---

## 🛠️ How to Use

1. Run either `spawer.py` (console) or `wsp.py` (GUI).
2. Enter the **number of messages** you want to send.
3. Quickly switch to the **WhatsApp chat window** of the person you want to message.
4. The script will start sending messages automatically. ✅

> ⚠️ **Note:** You need to switch to the WhatsApp window fast — the script begins after a short delay.

---

## 🔮 Roadmap

Support for more platforms is planned, including:

- 💬 WhatsApp
- 📱 SMS (Text Messages)
- 🎵 TikTok
- 📸 Instagram
- ...and more!

The goal is a unified manager where you only need to provide a **link** or **phone number**, and the tool will handle sending mass messages to any supported platform.

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use only**. Please use it responsibly and in accordance with each platform's terms of service. Spamming others without consent may violate laws or result in account bans.
