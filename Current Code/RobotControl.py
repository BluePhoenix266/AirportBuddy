import task_share
from LimitSwitch import *
from pyb import Pin
from time import ticks_ms
from time import ticks_diff


class TaskRobotControl:

    def __init__(self, dc_motor_top_right_flag: task_share.Share, stepper_motor_top_right_flag: task_share.Share):
        self.speed_tr = dc_motor_top_right_flag
        self.orientation_tr = stepper_motor_top_right_flag
        self.state = 0
        self.start_time = 0
        self.stop_time = 0
        self.count = 0

        self.speed = ""
        self.orientation = ""

        self.waiting_for = ""

        self.vcp = pyb.USB_VCP()

    def run(self):
        while True:
            if self.state == 0:
                if self.vcp.any():
                    self.vcp.read(1).decode()
                if self.orientation_tr.get() == 0:
                    self.state = 1
                    self.update(0, 0)
            elif self.state == 1:
                if self.vcp.any():
                    user_input = self.vcp.read(1).decode()
                    if self.waiting_for == "":
                        if user_input == 's':
                            self.waiting_for = "speed"
                            print("input desired speed")
                            pass
                        elif user_input == 'o':
                            self.waiting_for = "orientation"
                            print("input desired orientation")
                        else:
                            print("Invalid input. s: speed [rpm], o: orientation [deg]")
                            print("you typed: " + user_input)
                    elif self.waiting_for == "speed":
                        if user_input.isdigit():
                            self.speed += user_input
                            print("Current Input: " + str(self.speed))
                        else:
                            if user_input == '\x7f':
                                if len(self.speed) > 0:
                                    self.speed = self.speed[:-1]
                                    print("Current Input: " + str(self.speed))
                            elif user_input == '-' and len(self.speed) == 0:
                                self.speed += user_input
                                print("Current Input: " + str(self.speed))
                            elif user_input == '\r':
                                if len(user_input) > 0:
                                    self.update(int(self.speed), '')
                                    self.waiting_for = ""
                                    self.speed = ""
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)
                    elif self.waiting_for == "orientation":
                        if user_input.isdigit():
                            self.orientation += user_input
                            print("Current Input: " + str(self.orientation))
                        else:
                            if user_input == '\x7f':
                                if len(self.orientation) > 0:
                                    self.orientation = self.orientation[:-1]
                                    print("Current Input: " + str(self.orientation))
                            elif user_input == '-' and len(self.orientation) == 0:
                                self.orientation += user_input
                                print("Current Input: " + str(self.orientation))
                            elif user_input == '\r':
                                if len(user_input) > 0 and user_input != "-":
                                    self.update('', int(self.orientation))
                                    self.waiting_for = ""
                                    self.orientation = ""
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)
            else:
                print("Invalid State")
            yield self.state

    def update(self, robot_speed, robot_orientation):
        if robot_speed != '':
            if robot_speed > 60:
                self.speed_tr.put(60)
            elif robot_speed < -60:
                self.speed_tr.put(-60)
            else:
                self.speed_tr.put(robot_speed)
        if robot_orientation != '':
            if robot_orientation > 180:
                self.orientation_tr.put(180)
            elif robot_orientation < -180:
                self.orientation_tr.put(-180)
            else:
                self.orientation_tr.put(robot_orientation)
