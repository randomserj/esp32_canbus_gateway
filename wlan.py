import network

import misc

MODULE_NAME = 'WLAN'


class WLAN:
    def __init__(self):
        self.iface = network.WLAN(network.STA_IF)
        misc.LED_WLAN.off()

    def up(self):
        with open('wifi', 'r') as f:
            ssid, password = f.read().split('\n')
        if not self.iface.active() or not self.iface.isconnected():
            self.iface.active(True)
            misc.debug_print(MODULE_NAME, misc.PREFIX_INFO, 'Connecting to: {}'.format(ssid))
            self.iface.connect(ssid, password)
            while not self.iface.isconnected():
                pass
        misc.LED_WLAN.on()
        misc.debug_print(MODULE_NAME, misc.PREFIX_INFO, 'OK, got IP: {}'.format(self.iface.ifconfig()[0]))

    def down(self):
        if self.iface.isconnected():
            self.iface.disconnect()
            misc.LED_WLAN.off()
