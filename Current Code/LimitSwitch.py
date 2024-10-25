from pyb import Pin
import pyb


class LimitSwitch:
    '''!@brief A driver class for one channel of the L6206.
    @details Objects of this class can be used to apply PWM to a given
    DC motor on one channel of the L6206 from ST Microelectronics.
    '''

    def __init__(self, signal_pin):
        self.pin = Pin(signal_pin, mode=Pin.IN)
        self.signal_pin = pyb.ADC(self.pin)

    def get_state(self):
        if self.signal_pin.read() > 1000:
            return False
        else:
            return True


if __name__ == '__main__':
    switch = LimitSwitch(Pin.cpu.C0)
    while True:
        print(switch.get_state(), end='\r')
