import gc
import utime as time
from machine import SoftI2C

import canbus_trx as trx
import misc
from periphery import WLAN, OLED


def test():
    oled.print('Ready...')
    oled.print('AP: {}'.format(wifi.if_ap.ifconfig()[0]), 1)
    sta_ip = wifi.up()
    if sta_ip:
        oled.print('STA: {}'.format(sta_ip[0]), 2)


gc.collect()
wifi = WLAN()
tja = trx.CanBusDevice(misc.CAN_DEFAULT_SPEED)
oled = OLED(SoftI2C(scl=misc.PIN_OLED_SCL, sda=misc.PIN_OLED_SDA))