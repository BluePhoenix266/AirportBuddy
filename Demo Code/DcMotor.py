from pyb import Timer
from pyb import Pin
from time import ticks_ms
from time import ticks_diff


class DcMotor:
    '''!@brief A driver class for one channel of the L6206.
    @details Objects of this class can be used to apply PWM to a given
    DC motor on one channel of the L6206 from ST Microelectronics.
    '''

    def __init__(self, PWM_tim, IN1_pin, DIR1_pin, DIR2_pin, encoder):
        self.tim = Timer(PWM_tim, freq=1_000)
        self.IN1_pin = Pin(IN1_pin, mode=Pin.OUT_PP)
        self.DIR1_pin = Pin(DIR1_pin, mode=Pin.OUT_PP)
        self.DIR2_pin = Pin(DIR2_pin, mode=Pin.OUT_PP)
        self.DIR1_pin.low()
        self.DIR2_pin.low()
        self.duty = 0
        self.PWM_1 = self.tim.channel(1, pin=self.IN1_pin, mode=Timer.PWM, pulse_width_percent=self.duty)

        self.enc = encoder
        self.tmp_position = 0
        self.current_error = 0
        self.prop_term = 0
        self.integral_term = 0
        self.derivative_term = 0
        self.speed = 0
        self.last_error = 0
        self.error_slope = 0
        self.sum = 0
        self.rpm_delta = 0
        self.duty = 0
        self.e_sum = 0
        self.ki = 10
        self.kp = 50
        self.kp_term = 0
        self.ki_term = 0
        self.k_total = 0
        self.freq = 0
        self.desired_speed = 0

        self.first_run = True
        self.freq = 0
        self.time_start = 0
        self.time_stop = 0

    def set_duty(self, duty):
        if duty >= 0:
            self.PWM_1.pulse_width_percent(duty)
            self.DIR1_pin.high()
            self.DIR2_pin.low()
        else:
            self.PWM_1.pulse_width_percent(-duty)
            self.DIR1_pin.low()
            self.DIR2_pin.high()

    def set_speed(self, speed):
        self.desired_speed = speed

    def get_speed(self):
        return self.rpm_delta

    # def closed_loop(self,Kp,Ki,Kd,desired_speed,error,freq):
    def closed_loop(self, desired_speed):
        if self.first_run:
            self.enc.zero()
            self.time_start = ticks_ms()
            self.enc.update()
            self.first_run = False
        else:
            self.enc.update()
            self.time_stop = ticks_ms()
            self.freq = 1 / (ticks_diff(self.time_stop, self.time_start)) * 1000

            self.time_start = self.time_stop

            self.rpm_delta = self.enc.get_delta() * self.freq * 60 / 3200

            self.current_error = desired_speed - self.rpm_delta
            self.kp_term = -self.kp * self.current_error

            self.e_sum += self.current_error
            if self.e_sum > 50:
                self.e_sum = 50
            elif self.e_sum < -50:
                self.e_sum = -50

            self.ki_term = self.e_sum * -self.ki

            self.k_total = self.ki_term + self.kp_term

            self.duty = (self.k_total * 3200 / 60 / 1000)

            self.set_duty(self.duty)
            # print(self.duty)

if __name__ == '__main__':
    # dc_motor_top_right = DcMotor(1, Pin.cpu.A9, Pin.cpu.C7, Pin.cpu.A10, encoder_top_right, 0)
    mot = DcMotor(3, Pin.cpu.A9, Pin.cpu.A8, Pin.cpu.B10)
    mot.set_duty(0)
