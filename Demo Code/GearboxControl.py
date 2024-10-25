import task_share
from LimitSwitch import *
from pyb import Pin
from StepperMotor import *


class TaskGearboxControl:

    def __init__(self, velocity_flag: task_share.Share, rotation_flag: task_share.Share,
                 dc_motor, stepper_motor, limit_switch):

        self.rotation_flag = rotation_flag
        self.velocity_flag = velocity_flag

        self.dc_motor = dc_motor
        self.stepper_motor = stepper_motor
        self.limit_switch = limit_switch

        self.state = ""

        self.stepper_motor.en_pin.low()

    # The generator function that runs endlessly within this class
    def run(self):
        self.state = "Finding Home"
        while True:
            yield self.state
            if self.state == "Finding Home":
                # self.stepper_motor.en_pin.high()
                if self.limit_switch.get_state() or self.rotation_flag.get() == 0:
                    self.state = "Waiting"
                    self.rotation_flag.put(0)
                    self.stepper_motor.en_pin.low()
                else:
                    self.stepper_motor.step()
                    self.stepper_motor.en_pin.high()
            elif self.state == "Waiting":
                if (self.velocity_flag.get() != 0 or
                        self.stepper_motor.location-1.8 > self.rotation_flag.get() or
                        self.rotation_flag.get() > self.stepper_motor.location+1.8):
                    self.state = "Moving"
                else:
                    self.dc_motor.closed_loop(0)
                    self.stepper_motor.en_pin.low()
            elif self.state == "Moving":
                if (self.velocity_flag.get() == 0 and
                        self.stepper_motor.location-1.8 < self.rotation_flag.get() < self.stepper_motor.location+1.8):
                    self.state = "Waiting"
                    continue
                if not (self.stepper_motor.location-1.8 < self.rotation_flag.get() < self.stepper_motor.location+1.8):
                    self.stepper_motor.en_pin.high()
                    self.stepper_motor.move_to(self.rotation_flag.get())
                else:
                    self.stepper_motor.en_pin.low()
                self.dc_motor.closed_loop(self.velocity_flag.get())
            elif self.state == "Waiting":
                if (self.velocity_flag.get() == 0 or self.stepper_motor.location-1.8 > self.rotation_flag.get() or
                        self.stepper_motor.location + 1.8 < self.rotation_flag.get()):
                    self.state = "Moving"
            else:
                self.state = "Waiting"
