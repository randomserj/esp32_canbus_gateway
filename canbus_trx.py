from machine import CAN, UART
import _thread as thread

import misc

MODULE_NAME = 'CAN'


class CanBusDevice:
    class CanBusFrame:
        def __init__(self):
            self.id = 0
            self.dlc = 0
            self.data = []

    def __init__(self, speed):
        self.can = CAN(0, mode=CAN.NORMAL, baudrate=speed, tx_io=misc.PIN_CANBUS_TX, rx_io=misc.PIN_CANBUS_RX, auto_restart=False)
        self._reset(True)

    def _reset(self, debug=True):
        self.FLAG_RX_EXIT = True
        self.FLAG_TX_EXIT = True
        self.can.clear_rx_queue()
        self.can.clear_tx_queue()
        misc.LED_CANBUS_RX.off()
        misc.LED_CANBUS_TX.off()
        if debug:
            misc.debug_print(MODULE_NAME, misc.PREFIX_DEBUG, 'Reseted')

    def _thread_canbus_rx(self):
        while self.can.any() and not self.FLAG_RX_EXIT:
            frame = self.rx_frame()
            uart.write(bytearray(self.frame_to_string(frame) + '\n\r'))
        self.can.clear_rx_queue()
        misc.LED_CANBUS_RX.off()
        self.FLAG_RX_EXIT = True
        thread.exit()

    def rx_frame(self):
        try:
            frame = self.CanBusFrame()
            frame.id, *_, frame.data = self.can.recv()
            frame.dlc = len(frame.data)
            return frame
        except Exception as e:
            misc.debug_print(MODULE_NAME, misc.PREFIX_ERR, e)

    def rx(self, cmd=True):
        if not cmd or cmd == 0:
            self.FLAG_RX_EXIT = True
            return None
        if self.FLAG_RX_EXIT:
            self.FLAG_RX_EXIT = False
            misc.LED_CANBUS_RX.on()
            thread.start_new_thread(self._thread_canbus_rx, ())

    def tx(self, cmd=True, frames=[]):
        if not cmd or cmd == 0:
            misc.LED_CANBUS_TX.off()
            self.FLAG_TX_EXIT = True
            return None
        if self.FLAG_TX_EXIT:
            self.FLAG_TX_EXIT = False
            misc.LED_CANBUS_TX.on()
            # thread.start_new_thread(self.__thread_canbus_tx, (frames))

    def frame_to_string(self, frame):
        if isinstance(frame, self.CanBusFrame):
            frame_str = '{:03X} '.format(frame.id) + '{} '.format(frame.dlc) + ' '.join(['{:02X}'.format(b) for b in frame.data])
            return frame_str
        else:
            misc.debug_print(MODULE_NAME, misc.PREFIX_ERR, 'Wrong type of frame')


__can = CAN(0, mode=CAN.SILENT_LOOPBACK)        # init min CAN setup to avoid crash in twai.c :459
uart = UART(1, 115200)
