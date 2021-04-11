import network
import webrepl
from machine import UART
from machine import Pin
import _thread as thread
import canbus_trx as trx


LED_WIFI = Pin(2, Pin.OUT)
LED_CANBUS_RX = Pin(19, Pin.OUT)
LED_CANBUS_TX = Pin(21, Pin.OUT)

THREAD_CANBUS_RX_FLAG_EXIT = True
THREAD_CANBUS_TX_FLAG_EXIT = True


def init_state():
    global THREAD_CANBUS_RX_FLAG_EXIT
    THREAD_CANBUS_RX_FLAG_EXIT = True
    global THREAD_CANBUS_TX_FLAG_EXIT
    THREAD_CANBUS_TX_FLAG_EXIT = True
    LED_WIFI.off()
    LED_CANBUS_RX.off()
    LED_CANBUS_TX.off()
    tja.can.clear_rx_queue()
    tja.can.clear_tx_queue()


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


def thread_canbus_rx():
    while tja.can.any() and not THREAD_CANBUS_RX_FLAG_EXIT:
        frame = tja.rx_frame()
        uart.write(bytearray(tja.frame_to_string(frame) + '\n\r'))
    tja.can.clear_rx_queue()
    LED_CANBUS_RX.off()
    thread.exit()


def dev_ctrl(cmd, param=None):
    if cmd == 'reset':
        init_state()
    if cmd == 'wifi':
        wlan_connect()
    if cmd == 'rx_stop':
        global THREAD_CANBUS_RX_FLAG_EXIT
        THREAD_CANBUS_RX_FLAG_EXIT = True
    if cmd == 'rx':
        global THREAD_CANBUS_RX_FLAG_EXIT
        THREAD_CANBUS_RX_FLAG_EXIT = False
        LED_CANBUS_RX.on()
        thread.start_new_thread(thread_canbus_rx, ())
    if cmd == 'tx':
        print(param)
    if cmd == 'exit':
        uart.sendbreak()
    if cmd == 'test':
        uart.write(bytearray('it is still alive\n\r'))
    print(cmd)


webrepl.start()
tja = trx.CanBusDevice()
uart = UART(1, 115200, tx=17, rx=16)
