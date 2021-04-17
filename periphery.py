import network
import framebuf
from micropython import const

import misc


# TODO:
# make the AP secure
# add sort of wifi manager
class WLAN:
    def __init__(self):
        self.MODULE_NAME = 'WLAN'
        self.if_sta = network.WLAN(network.STA_IF)
        self.if_ap = network.WLAN(network.AP_IF)
        self.if_ap.config(essid='gateway')
        self._reset()

    def _reset(self):
        self.if_sta.active(False)
        self.if_ap.active(True)
        misc.LED_WLAN.off()
        misc.debug_print(self.MODULE_NAME, misc.PREFIX_DEBUG, 'Reseted')
        misc.debug_print(self.MODULE_NAME, misc.PREFIX_INFO, 'AP IP: {}'.format(self.if_ap.ifconfig()[0]))

    def _stop(self):
        self.if_sta.active(False)
        self.if_ap.active(False)
        misc.debug_print(self.MODULE_NAME, misc.PREFIX_INFO, 'Stopped')

    def up(self):
        if not self.if_sta.active() or not self.if_sta.isconnected():
            try:
                f = open(misc.WIFI_FILE, 'r')
                ssid, password, *_ = f.read().split(' ')
                self.if_sta = network.WLAN(network.STA_IF)
                misc.debug_print(self.MODULE_NAME, misc.PREFIX_INFO, 'Connecting to: {}'.format(ssid))
                self.if_sta.active(True)
                self.if_sta.connect(ssid, password)
                while not self.if_sta.isconnected():
                    pass
                misc.LED_WLAN.on()
                misc.debug_print(self.MODULE_NAME, misc.PREFIX_INFO, 'OK, IP: {}'.format(self.if_sta.ifconfig()[0]))
                return self.if_sta.ifconfig()
            except Exception as e:
                misc.debug_print(self.MODULE_NAME, misc.PREFIX_DEBUG, e)

    def down(self):
        if self.if_sta.active():
            self.if_sta.active(False)
            misc.debug_print(self.MODULE_NAME, misc.PREFIX_INFO, 'WiFi interface deactivated')
            misc.LED_WLAN.off()


# TODO:
# add cursor
class OLED:
    def __init__(self, i2c, width=128, height=64, addr=0x3c, external_vcc=False):
        self.MODULE_NAME = 'OLED'
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self._reset()

    def _reset(self):
        self.fb.fill(0)
        self.power_on()
        self.show()
        misc.debug_print(self.MODULE_NAME, misc.PREFIX_DEBUG, 'Reseted')

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)

    def power_off(self):
        self.write_cmd(const(0xae) | 0x00)

    def power_on(self):
        self.write_cmd(const(0xae) | 0x01)

    def show(self):
        for page in range(self.height // 8):
            self.write_cmd(const(0xb0) | page)
            self.write_cmd(const(0x00) | 2)
            self.write_cmd(const(0x10) | 0)
            self.write_data(self.buffer[self.width * page:self.width * page + self.width])

    def print(self, text='', line=0, pos=0):
        self.fb.text(text, pos*misc.FONT, line*misc.FONT)
        self.show()

    def clear(self, line=0, pos=0, count=1):
        self.fb.fill_rect(pos*misc.FONT, line*misc.FONT, count*misc.FONT, misc.FONT, 0)
        self.show()

    def clear_line(self, n=-1):
        self.clear(n, 0, 16)
