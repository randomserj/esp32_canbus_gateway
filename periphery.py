import network
import framebuf
from micropython import const
from machine import CAN
import _thread as thread

import misc


# TODO:
# make the AP secure
# add sort of wifi manager
class WLAN:
    def __init__(self):
        self.MODULE_NAME = 'WLAN'
        self.if_sta = network.WLAN(network.STA_IF)
        self.if_ap = network.WLAN(network.AP_IF)
        self.if_ap.active(True)
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
            except Exception as e:
                misc.debug_print(self.MODULE_NAME, misc.PREFIX_DEBUG, e)
        return self.if_sta.ifconfig()

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
        self.power_off()
        self.power_on()
        self.fb.fill(0)
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

    def cls(self):
        self.fb.fill(0)
        self.show()

    def print(self, text='', line=0, pos=0):
        self.fb.text(text, pos*misc.FONT, line*misc.FONT)
        self.show()

    def clear(self, line=0, pos=0, count=1):
        self.fb.fill_rect(pos*misc.FONT, line*misc.FONT, count*misc.FONT, misc.FONT, 0)
        self.show()

    def clear_line(self, line):
        self.clear(line, 0, 16)

    def clear_lines(self, lines=()):
        for line in lines:
            self.clear_line(line)


class CANTRX:
    def __init__(self, speed, output):
        self.MODULE_NAME = 'CAN'
        self.can = CAN(0, mode=CAN.NORMAL, baudrate=speed, tx_io=misc.PIN_CANBUS_TX, rx_io=misc.PIN_CANBUS_RX, auto_restart=False)
        self.output = output
        self._reset(True)

    def _reset(self, debug=True):
        self.FLAG_RX_EXIT = True
        self.FLAG_TX_EXIT = True
        self.can.clear_rx_queue()
        self.can.clear_tx_queue()
        misc.LED_CANBUS_RX.off()
        misc.LED_CANBUS_TX.off()
        if debug:
            misc.debug_print(self.MODULE_NAME, misc.PREFIX_DEBUG, 'Reseted')

    def _thread_canbus_rx(self):
        while self.can.any() and not self.FLAG_RX_EXIT:
            msg = self.rx_msg()
            self.output.write(bytearray(msg + '\n\r'))
        self.can.clear_rx_queue()
        misc.LED_CANBUS_RX.off()
        self.FLAG_RX_EXIT = True
        thread.exit()

    def _thread_canbus_tx(self, ms):
        while not self.FLAG_TX_EXIT:
            try:
                for m in ms:
                    m_id, m_dlc, *m_data = m.split(' ')
                    self.can.send([int(d, 16) for d in m_data], int(m_id, 16))
            except Exception as e:
                misc.debug_print(self.MODULE_NAME, misc.PREFIX_ERR, e)
                break
        self.can.clear_tx_queue()
        misc.LED_CANBUS_TX.off()
        self.FLAG_TX_EXIT = True
        thread.exit()

    def rx_msg(self):
        try:
            msg_id, *_, msg_data = self.can.recv()
            msg_dlc = len(msg_data)
            msg = '{:03X} '.format(msg_id) + '{} '.format(msg_dlc) + ' '.join(['{:02X}'.format(b) for b in msg_data])
            return msg
        except Exception as e:
            misc.debug_print(self.MODULE_NAME, misc.PREFIX_ERR, e)

    def rx(self, cmd=True):
        if not cmd or cmd == 0:
            self.FLAG_RX_EXIT = True
            return None
        if self.FLAG_RX_EXIT:
            self.FLAG_RX_EXIT = False
            misc.LED_CANBUS_RX.on()
            thread.start_new_thread(self._thread_canbus_rx, ())
            return None

    def tx(self, cmd=True, msgs=None):
        if not cmd or cmd == 0:
            self.FLAG_TX_EXIT = True
            return None
        if self.FLAG_TX_EXIT:
            self.FLAG_TX_EXIT = False
            misc.LED_CANBUS_TX.on()
            thread.start_new_thread(self._thread_canbus_tx, (msgs,))
            return None
