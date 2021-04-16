import gc
import utime as time

from machine import SoftI2C
import canbus_trx as trx
import wlan
# import sh1106

MODULE_NAME = 'MAIN'
SEC = 1000
CAN_DEFAULT_SPEED = 500

gc.collect()
time.sleep_ms(SEC)
wifi = wlan.WLAN()
tja = trx.CanBusDevice(CAN_DEFAULT_SPEED)

# oled = sh1106.SH1106_I2C(128, 64, SoftI2C(scl=PIN_I2C_SCL, sda=PIN_I2C_SDA))
# oled.rotate(1)

