import misc
from machine import CAN

MODULE_NAME = 'CAN BUS'

TX_IO = 5
RX_IO = 4


class CanBusDevice:
    def __init__(self):
        self.can = CAN(
            0,
            extframe=False,
            mode=CAN.NORMAL,
            baudrate=CAN.BAUDRATE_500k,
            tx_io=TX_IO,
            rx_io=RX_IO,
            auto_restart=False,
        )

    class CanBusFrame:
        def __init__(self):
            self.id = 0
            self.dlc = 0
            self.data = []

    def rx_frame(self):
        try:
            frame = self.CanBusFrame()
            frame.id, *_, frame.data = self.can.recv()
            frame.dlc = len(frame.data)
            return frame
        except Exception as e:
            misc.debug_print(MODULE_NAME, misc.PREFIX_W, e)

    def frame_to_string(self, frame):
        if isinstance(frame, self.CanBusFrame):
            frame_str = '{:03X} '.format(frame.id) + '{} '.format(frame.dlc) + ' '.join(['{:02X}'.format(b) for b in frame.data])
            return frame_str
        else:
            misc.debug_print(MODULE_NAME, misc.PREFIX_E, 'Wrong type of frame')
