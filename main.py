import gc
import network
import webrepl
from machine import UART, Pin, I2C
import _thread as thread
import canbus_trx as trx
import sh1106
import misc

MODULE_NAME = 'MAIN'

PIN_I2C_SCK = Pin(22)
PIN_I2C_SDA = Pin(21)
LED_WIFI = Pin(2, Pin.OUT)


def wlan_connect(ssid='Somewifi', password='iwannawifi'):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        print('connecting to:', ssid)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    LED_WIFI.on()
    print('network config:', wlan.ifconfig())


gc.collect()
webrepl.start()

oled = sh1106.SH1106_I2C(128, 64, I2C(-1, scl=PIN_I2C_SCK, sda=PIN_I2C_SDA))
tja = trx.CanBusDevice()
