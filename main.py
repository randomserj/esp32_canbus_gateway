import gc
import machine
from machine import SoftI2C, UART
import usocket as socket

import misc
from periphery import WLAN, OLED, CANTRX


MODULE_NAME = 'MAIN'


# 76543210
def get_bit(number, n):
    bit = (number & (1 << n)) >> n
    return bit


def check_frame(frame):
    pass


def parse_frame(frame):
    try:
        data = frame.decode('utf-8')
        # TODO:
        # check frame structure and checksum
        # check if cmd is bin or hex
    except Exception as e:
        misc.debug_print(MODULE_NAME, misc.PREFIX_ERR, e)
    finally:
        cmd_bytes = [int(data[i:i + 2], 16) for i in range(0, len(data), 2)]
        handshake = get_bit(cmd_bytes[0], 7)
        checksum = get_bit(cmd_bytes[0], 0)
        if not (handshake ^ checksum):
            respond = misc.TERMINATE
        elif handshake:
            respond = cmd_bytes[0] ^ misc.MASK
        else:
            respond = misc.ACK
        return respond, cmd_bytes


def run_cmd(cmd_bytes):
    mode = get_bit(cmd_bytes[0], 6)
    if mode:
        cfg = (cmd_bytes[0] & 0x30) >> 4
        if cfg == 0b11:
            machine.reset()
        if cfg == 0b01:
            trx._reset()
        if cfg == 0b10:
            show_wlan_connectivity()
        if cfg == 0b00:
            oled.cls()
    else:
        is_rx = get_bit(cmd_bytes[0], 5)
        is_tx = get_bit(cmd_bytes[0], 4)
        if is_rx:
            trx.rx()
        else:
            trx.rx(False)
        if is_tx:
            trx.tx(msgs=['3D0 8 00 80 00 00 00 00 00 00', '280 8 49 0E 00 10 0E 00 1B 0E'])
        else:
            trx.tx(False)


def start(ip_addr='0.0.0.0'):
    socket_server = socket.socket()
    addr = socket.getaddrinfo(ip_addr, 9871)[0][-1]
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind(addr)
    socket_server.listen(5)
    FLAG_SS_OPEN = True
    while FLAG_SS_OPEN:
        client = socket_server.accept()
        stream = client[0]
        while True:
            frame = stream.recv(128)
            oled.clear_lines(SOCK_LINES)
            respond, payload = parse_frame(frame)
            oled.print('0x{:X} 0x{:0>8b}'.format(respond, payload[0]), SOCK_LINES[0])
            misc.debug_print(MODULE_NAME, misc.PREFIX_DEBUG, 'Respond: 0x{:X} cmd: {:0>8b}'.format(respond, payload[0]))
            stream.send(hex(respond)[2:].encode('utf-8'))
            if respond == misc.TERMINATE:
                if payload[0] == 0xff:
                    FLAG_SS_OPEN = False
                break
            run_cmd(payload)
        stream.close()
    socket_server.close()


def show_wlan_connectivity():
    oled.clear_lines(WLAN_LINES)
    oled.print('AP: {}'.format(wifi.if_ap.ifconfig()[0]), 0)
    sta_ip = wifi.up()[0]
    if sta_ip != '0.0.0.0':
        oled.print('STA: {}'.format(sta_ip), 1)


WLAN_LINES = [0, 1]
SOCK_LINES = [3, 4]
CAN_LINES = [6, 7]

gc.collect()
wifi = WLAN()
oled = OLED(SoftI2C(scl=misc.PIN_OLED_SCL, sda=misc.PIN_OLED_SDA))
uart = UART(2, 115200)  # rx to esp.io17, tx to esp.io16
####################################################
# init min CAN setup to avoid crash in twai.c :459
__can = machine.CAN(0, mode=machine.CAN.SILENT_LOOPBACK)
####################################################
trx = CANTRX(misc.CAN_DEFAULT_SPEED, uart)

oled.cls()
# TODO:
# use oled for statuses
show_wlan_connectivity()
start()
