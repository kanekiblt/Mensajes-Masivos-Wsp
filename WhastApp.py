import pyautogui as pg
import time

msjs = int(input("Número de mensajes: "))
ms = "" <---#Escribe el mensaje que quieres enviar

time.sleep(3)

for i in range(msjs):
   
    pg.write(ms)
    #pg.write(msj)
    
    pg.press('enter')
