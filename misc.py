from machine import Pin


PIN_CANBUS_RX = 4
PIN_CANBUS_TX = 5
PIN_UART_RX = 16
PIN_UART_TX = 17
PIN_OLED_SCL = Pin(22)
PIN_OLED_SDA = Pin(21)

LED_WLAN = Pin(32, Pin.OUT)
LED_CANBUS_RX = Pin(19, Pin.OUT)
LED_CANBUS_TX = Pin(23, Pin.OUT)

PREFIX_INFO = 'INFO'
PREFIX_WARN = 'WARNING'
PREFIX_ERR = 'ERROR'
PREFIX_DEBUG = 'DEBUG'
PREFIXES = [PREFIX_INFO, PREFIX_WARN, PREFIX_ERR, PREFIX_DEBUG]

WIFI_FILE = 'wifi'
MASK = 0xff
ACK = 0x55
TERMINATE = 0xaa
CAN_DEFAULT_SPEED = 500
FONT = 8


# TODO:
# add debug option, rename to dprint
def debug_print(module, prefix, text):
    if module is not None and prefix in PREFIXES:
        print('[{}]\t***\t{}\t***\t{}'.format(module, prefix, text))
    else:
        raise TypeError("Wrong usage of debug_print")
