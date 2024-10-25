from pyb import *
from pyb import Pin
from pyb import Timer
import time


class ServoMotor:
    def __init__(self, pwm_tim, control_pin):
        self.tim = Timer(pwm_tim, freq=50)
        self.control_pin = Pin(control_pin, mode=Pin.OUT_PP)

        self.duty = 0
        self.pwm = self.tim.channel(1, pin=self.control_pin, mode=Timer.PWM, pulse_width_percent=self.duty)
        self.lower_limit = 3.2
        self.upper_limit = 15
        self.range = 180
        self.mid_position = 7.5

    def sd(self, duty):
        if duty > 50:
            self.pwm.pulse_width_percent(50)
        elif duty < 0:
            self.pwm.pulse_width_percent(0)
        else:
            self.pwm.pulse_width_percent(duty)

    def sr(self, rotation):
        if rotation >= 180:
            self.pwm.pulse_width_percent(self.upper_limit)
        elif rotation <= 0:
            self.pwm.pulse_width_percent(self.lower_limit)
        # elif rotation < 90:
        #     new_duty = self.lower_limit + (self.mid_position - self.lower_limit) / self.range * rotation
        #     self.pwm.pulse_width_percent(new_duty)
        else:
            new_duty = self.upper_limit / self.range * rotation
            self.pwm.pulse_width_percent(new_duty)


if __name__ == '__main__':
    m = ServoMotor(3, Pin.cpu.B4)

