import time
import network

try:
  import urequests as requests
except:
  import requests
  
try:
  import ujson as json
except:
  import json
  
import framebuf
from machine import Pin, ADC, SPI

import texgyread30 as texgyread_L # fonte de grande taille
import texgyread20 as texgyread_S # fonte de petite taille

from epaper import EPD

led = Pin("LED", Pin.OUT)
led.value(1) # LED On
led.value(0) # LED Off

# Display resolution
EPD_WIDTH  = 400
EPD_HEIGHT = 300

rst = Pin(12)
dc = Pin(8)
cs = Pin(9)
busy = Pin(13)
spi = SPI(1)
spi.init(baudrate=4000_000)

# initialiser l'objet écran
epd = EPD(spi, cs, dc, rst, busy)
epd.init()
buf = bytearray(EPD_HEIGHT * EPD_WIDTH)
# créer le tampon et le remplir avec du blanc
fb = framebuf.FrameBuffer(buf, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)
fb.fill(0xff)

# fonction d'ajout de texte dans le buffer
def writetext(fb, font, posx, posy, text, invert=False, format=framebuf.MONO_HMSB, key=1):
    x = posx
    fheight = font.height()
    for letter in text:
        glyph, height, width = font.get_ch(letter)
        buf = bytearray(glyph)

        if not invert:
            for i, v in enumerate(buf):
                buf[i] = 0xFF & ~ v

        frm = framebuf.FrameBuffer(buf, width, height, format)
        fb.blit(frm, x, posy + (fheight - height), key)
        x += width

# Connexion au Wifi
ssid='MON_SSID' # => mettre ici votre SSID
password='MON_PASSWORD' # => mettre ici votre mot de passe Wifi

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Attente de la connexion (ou échec)
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Prendre en charge l'échec de connexion
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    s = 3
    while s > 0:
        s -= 1
        led.value(1)
        time.sleep(0.5)
        led.value(0)
        time.sleep(0.5)
        
    status = wlan.ifconfig()
    print( 'Connected to ' + ssid + '. ' + 'Device IP: ' + status[0] )
    

# Lancer une requête HTTP (GET) vers une API
api_data = requests.get("http://swapi.dev/api/people/46")
name = api_data.json()['name']

# Afficher le résultat sur l'écran ePaper, en deux étapes

writetext(fb, texgyread_L, 15, 40, name) # ajouter le texte au tampon 
epd.display_frame(buf) # rafraîchir l'écran
time.sleep(2)