import pyautogui as pg
import time

num = int(input("Número de mensajes: "))
msj = "" <---#Escribe el mensaje que quieres enviar

time.sleep(3)

for i in range(num):
   
    pg.write(msj)

    
    pg.press('enter')
