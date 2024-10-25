from pyb import *
from pyb import Pin
import pyb
import time


class StepperMotor:
    def __init__(self, step_pin, dir_pin, en_pin):
        self.step_pin = Pin(step_pin, mode=Pin.OUT_PP)
        self.dir_pin = Pin(dir_pin, mode=Pin.OUT_PP)
        self.en_pin = Pin(en_pin, mode=Pin.OUT_PP)

        self.step_pin.low()
        self.dir_pin.low()
        self.en_pin.low()

        self.location = 0

    def step(self):
        self.step_pin.high()
        time.sleep(0.0005)
        self.step_pin.low()
        time.sleep(0.0005)

    def dir(self, direction):
        if direction == 0:
            self.dir_pin.low()
        if direction == 1:
            self.dir_pin.high()

    def move_to(self, desired_location):
        # self.en_pin.high()
        if self.location < desired_location:
            self.dir(0)
            self.step()
            self.location += 1.8
        elif self.location > desired_location:
            self.dir(1)
            self.step()
            self.location -= 1.8
        else:
            pass
        # self.en_pin.low()

    def rev(self):
        count = 0
        while count < 200:
            self.step()
            time.sleep(0.001)
            count += 1

    def reset(self):
        pass


if __name__ == '__main__':
    mot = StepperMotor(Pin.cpu.A0, Pin.cpu.A1, Pin.cpu.A2)
    # step_pin = Pin(Pin.cpu.A0, mode=Pin.OUT_PP)
    # dir_pin = Pin(Pin.cpu.A1, mode=Pin.OUT_PP)
    # while True:
    #     mot.step()
    #     time.sleep(0.01)
    #     # for x in range(500):
    #     time.sleep(0.0005)
    #     step_pin.high()
    #     time.sleep(0.0005)
    #     step_pin.low()
    #         # time.sleep(0.0005)
