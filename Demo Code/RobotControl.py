import task_share
from LimitSwitch import *
from ServoMotor import *
from pyb import Pin
from time import ticks_ms
from time import ticks_diff
import math


class TaskRobotControl:

    def __init__(self, dc_mot_bl_flg, step_mot_bl_flg,
                 dc_mot_br_flg, step_mot_br_flg,
                 dc_mot_fl_flg, step_mot_fl_flg,
                 dc_mot_fr_flg, step_mot_fr_flg):

        # Gearbox Motor Flags, self.orientation_x.put(0) sets the gearbox so that it does not look for home
        self.speed_bl = dc_mot_bl_flg
        self.orientation_bl = step_mot_bl_flg
        # self.orientation_bl.put(0)
        self.speed_br = dc_mot_br_flg
        self.orientation_br = step_mot_br_flg
        self.orientation_br.put(0)
        self.speed_fl = dc_mot_fl_flg
        self.orientation_fl = step_mot_fl_flg
        self.orientation_fl.put(0)
        self.speed_fr = dc_mot_fr_flg
        self.orientation_fr = step_mot_fr_flg
        self.orientation_fr.put(0)
        self.servo = ServoMotor(4, Pin.cpu.B6)
        self.data_count = 0

        # Specifies the operation mode of the robot defined in state 0 after home has been found by gearboxes
        self.state = 0
        self.start_time = 0
        self.stop_time = 0

        # Used to specify desired speed and orientation of each motor of gearbox
        self.speed = ""
        self.orientation = ""

        # Used to determine desired position and final orientation of the robot
        self.x = ""
        self.y = ""
        self.robot_orientation = ""

        # Mini state specifications
        self.waiting_for = ""
        self.movement_stage = ""

        # Used to read inputs from the computer to the nucleo
        self.vcp = pyb.USB_VCP()

        # Robot Physical Properties
        self.dc_mot_gear_ratio = 1
        self.step_mot_gear_ratio = 1
        self.wheel_size = 2/12 # feet
        self.wheel_distance_x = 4.25/12 # feet
        self.wheel_distance_y = 4.25/12 # feet
        self.wheel_linear_velocity = 60 * 2 * 3.14 * self.wheel_size / 60 # ft / second
        # self.wheel_angular_velocity = (self.wheel_linear_velocity /
        #                                math.sqrt(self.wheel_distance_x^2 + self.wheel_distance_y^2) *
        #                                180 / 3.1415) # degrees / s
        self.wheel_angle_for_movement = 0 # degrees

        # Variables for Robot Move Distance
        self.robot_move_distance = 0 # feet

    def run(self):
        while True:
            # Find Home Then Set the robot operating state via the self.state attribute
            if self.state == 0:
                if self.vcp.any():
                    self.vcp.read(1).decode()
                if self.orientation_bl.get() == 0:
                    # Hard Code the desired state into the line below. 1 Was used for demo presentation
                    self.state = 1
                    if self.state == 3:
                        print("Please input x")
                        self.waiting_for = "x"
                    self.update(0, 0, self.speed_bl, self.orientation_bl)

            # Direct Motor Control State
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
                        elif user_input == 'g':
                            self.start_time = ticks_ms()
                            self.stop_time = ticks_ms()
                            print("closing grabber")
                            while ticks_diff(self.stop_time, self.start_time) / 1000 < 1:
                                if self.vcp.any():
                                    user_input = self.vcp.read(1).decode()
                                    print("wait for grabber, you pressed: " + str(user_input))
                                self.servo.sd(5)
                                self.stop_time = ticks_ms()
                                yield self.state
                            self.servo.sd(0)
                            print("done closing")
                        elif user_input == 'u':
                            self.start_time = ticks_ms()
                            self.stop_time = ticks_ms()
                            print("opening grabber")
                            while ticks_diff(self.stop_time, self.start_time) / 1000 < 1:
                                if self.vcp.any():
                                    user_input = self.vcp.read(1).decode()
                                    print("wait for grabber, you pressed: " + str(user_input))
                                self.servo.sd(10)
                                self.stop_time = ticks_ms()
                                yield self.state
                            self.servo.sd(0)
                            print("done opening")
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
                                    self.update(int(self.speed), '', self.speed_bl, self.orientation_bl)
                                    # self.update(int(self.speed), '', self.speed_fl, self.orientation_fl)
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
                                    self.update('', int(self.orientation), self.speed_bl, self.orientation_bl)
                                    # self.update('', int(self.orientation), self.speed_fl, self.orientation_fl)
                                    self.waiting_for = ""
                                    self.orientation = ""
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)

            # Direct Robot Control State
            elif self.state == 2:
                if self.vcp.any():
                    user_input = self.vcp.read(1).decode()
                    if user_input == 'w':
                        self.update(0, 60, self.speed_bl, self.orientation_bl)
                    elif user_input == 'a':
                        self.update(90, 60, self.speed_bl, self.orientation_bl)
                    elif user_input == 's':
                        self.update(180, 60, self.speed_bl, self.orientation_bl)
                    elif user_input == 'd':
                        self.update(-90, 60, self.speed_bl, self.orientation_bl)
                    elif user_input == 'q':
                        self.update(-45, 60, self.speed_bl, self.orientation_bl)
                    elif user_input == 'e':
                        self.update(45, 60, self.speed_bl, self.orientation_bl)
                    else:
                        print("Invalid input. Use keys [w,a,s,d,q,e]")
                        print("you typed: " + user_input)

            # Input Desired Location and Speed
            elif self.state == 3:
                if self.vcp.any():
                    user_input = self.vcp.read(1).decode()

                    if self.waiting_for == "x":
                        if user_input.isdigit():
                            self.x += user_input
                            print("Current Input: " + str(self.x))
                        else:
                            if user_input == '\x7f':
                                if len(self.x) > 0:
                                    self.x = self.x[:-1]
                                    print("Current Input: " + str(self.x))
                            elif user_input == '-' and len(self.x) == 0:
                                self.x += user_input
                                print("Current Input: " + str(self.x))
                            elif user_input == '\r':
                                if len(self.x) > 0:
                                    self.update(int(self.x), '', self.speed_bl, self.orientation_bl)
                                    self.waiting_for = "y"
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)

                    elif self.waiting_for == "y":
                        if user_input.isdigit():
                            self.y += user_input
                            print("Current Input: " + str(self.y))
                        else:
                            if user_input == '\x7f':
                                if len(self.y) > 0:
                                    self.y = self.y[:-1]
                                    print("Current Input: " + str(self.y))
                            elif user_input == '-' and len(self.y) == 0:
                                self.y += user_input
                                print("Current Input: " + str(self.y))
                            elif user_input == '\r':
                                if len(self.y) > 0:
                                    self.update(int(self.y), '', self.speed_bl, self.orientation_bl)
                                    self.waiting_for = "robot_orientation"
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)

                    elif self.waiting_for == "robot_orientation":
                        if user_input.isdigit():
                            self.robot_orientation += user_input
                            print("Current Input: " + str(self.robot_orientation))
                        else:
                            if user_input == '\x7f':
                                if len(self.robot_orientation) > 0:
                                    self.robot_orientation = self.robot_orientation[:-1]
                                    print("Current Input: " + str(self.robot_orientation))
                            elif user_input == '-' and len(self.robot_orientation) == 0:
                                self.robot_orientation += user_input
                                print("Current Input: " + str(self.robot_orientation))
                            elif user_input == '\r':
                                if len(self.robot_orientation) > 0:
                                    self.wheel_angle_for_movement = math.degrees(math.atan(int(self.y)/int(self.x)))
                                    self.robot_move_distance = math.sqrt(int(self.x)^2 + int(self.y)^2)
                                    self.waiting_for = "Rotation Prep"
                                else:
                                    print("No input not valid")
                            else:
                                print("invalid input, only digits accepted")
                                print("you typed: " + user_input)

                    elif self.movement_stage == "Rotation Prep":
                        self.update(0, 45, self.speed_bl, self.orientation_bl)
                        self.update(0, -45, self.speed_br, self.orientation_br)
                        self.update(0, 45, self.speed_fl, self.orientation_fl)
                        self.update(0, -45, self.speed_fr, self.orientation_fr)
                        # include delay based on testing to allow wheels to get into position
                        self.movement_stage = "Rotate Robot"
                        self.start_time = ticks_ms()

                    elif self.movement_stage == "Rotate Robot":
                        self.stop_time = ticks_ms()
                        if int(self.robot_orientation) > 0:
                            self.update(-60, '', self.speed_bl, self.orientation_bl)
                            self.update(-60, '', self.speed_br, self.orientation_br)
                            self.update(-60, '', self.speed_fl, self.orientation_fl)
                            self.update(-60, '', self.speed_fr, self.orientation_fr)
                        else:
                            self.update(60, '', self.speed_bl, self.orientation_bl)
                            self.update(60, '', self.speed_br, self.orientation_br)
                            self.update(60, '', self.speed_fl, self.orientation_fl)
                            self.update(60, '', self.speed_fr, self.orientation_fr)
                        if (ticks_diff(self.stop_time, self.start_time) / 1000 >
                                self.wheel_angular_velocity * int(self.robot_orientation)):
                            self.movement_stage = "Moving Robot Prep"

                    elif self.movement_stage == "Moving Robot Prep":
                        # Do math to determine wheel_orientation angle
                        self.update(0, self.wheel_angle_for_movement-self.robot_orientation, self.speed_bl, self.orientation_bl)
                        self.update(0, self.wheel_angle_for_movement-self.robot_orientation, self.speed_br, self.orientation_br)
                        self.update(0, self.wheel_angle_for_movement-self.robot_orientation, self.speed_fl, self.orientation_fl)
                        self.update(0, self.wheel_angle_for_movement-self.robot_orientation, self.speed_fr, self.orientation_fr)
                        # edit delay based on testing to allow wheels to get into position
                        if ticks_diff(self.stop_time, self.start_time) / 1000 > 0.5:
                            self.grab_suitcase()
                            self.movement_stage = "Rotate Robot"
                            self.start_time = ticks_ms()

                    elif self.movement_stage == "Move Robot":
                        self.update(60, '', self.speed_bl, self.orientation_bl)
                        self.update(60, '', self.speed_br, self.orientation_br)
                        self.update(60, '', self.speed_fl, self.orientation_fl)
                        self.update(60, '', self.speed_fr, self.orientation_fr)
                        self.stop_time = ticks_ms()
                        # include math here to move robot to correct location replace the 1 with calculated value
                        if (ticks_diff(self.stop_time, self.start_time) / 1000 >
                                self.robot_move_distance * self.wheel_linear_velocity):
                            # include delay to give grabber time to grab the suitcase
                            self.movement_stage = ""
                            self.waiting_for = "Final Movement Prep"

                    elif self.movement_stage == "Final Movement Prep":
                        # Do math to determine wheel_orientation angle
                        self.update(0, 0, self.speed_bl, self.orientation_bl)
                        self.update(0, 0, self.speed_br, self.orientation_br)
                        self.update(0, 0, self.speed_fl, self.orientation_fl)
                        self.update(0, 0, self.speed_fr, self.orientation_fr)
                        # edit delay based on testing to allow wheels to get into position
                        if ticks_diff(self.stop_time, self.start_time) / 1000 > 0.5:
                            self.movement_stage = "Final Movement"
                            self.start_time = ticks_ms()

                    elif self.movement_stage == "Final Movement":
                        # Do math to determine wheel_orientation angle
                        self.update(60, 0, self.speed_bl, self.orientation_bl)
                        self.update(60, 0, self.speed_br, self.orientation_br)
                        self.update(60, 0, self.speed_fl, self.orientation_fl)
                        self.update(60, 0, self.speed_fr, self.orientation_fr)
                        # edit delay based on testing to allow wheels to get into position
                        if ticks_diff(self.stop_time, self.start_time) / 1000 > self.wheel_linear_velocity * 1:
                            self.update(0, 0, self.speed_bl, self.orientation_bl)
                            self.update(0, 0, self.speed_br, self.orientation_br)
                            self.update(0, 0, self.speed_fl, self.orientation_fl)
                            self.update(0, 0, self.speed_fr, self.orientation_fr)
                            self.grab_suitcase()
                            self.movement_stage = "New Input"
                            self.start_time = 0

                    elif self.waiting_for == "New Input":
                        if self.vcp.any():
                            user_input = self.vcp.read(1).decode()
                            if user_input == '\r':
                                self.update(0, 0, self.speed_bl, self.orientation_bl)
                                self.x = ""
                                self.y = ""
                                self.robot_orientation = ""
                                self.waiting_for = ""

            # Path Planning Control Given from outside source (topside laptop)
            elif self.state == 4:
                if self.vcp.any():
                    user_input = self.vcp.read(1).decode()
                    if self.count == 0:
                        self.update(user_input[0], user_input[1], self.speed_bl, self.orientation_bl)
                    elif self.count == 1:
                        self.update(user_input[0], user_input[1], self.speed_br, self.orientation_br)
                    elif self.count == 2:
                        self.update(user_input[0], user_input[1], self.speed_fl, self.orientation_fl)
                    elif self.count == 3:
                        self.update(user_input[0], user_input[1], self.speed_fr, self.orientation_fr)
                    self.count += 1

            else:
                print("Invalid State")


            yield self.state

    def update(self, wheel_speed, wheel_orientation, speed, orientation):
        if wheel_speed != '':
            if wheel_speed > 60:
                speed.put(60)
            elif wheel_speed < -60:
                speed.put(-60)
            else:
                speed.put(wheel_speed)
        if wheel_orientation != '':
            if wheel_orientation > 180:
                orientation.put(180)
            elif wheel_orientation < -180:
                orientation.put(-180)
            else:
                orientation.put(wheel_orientation)

    def grab_suitcase(self):
        suitcase_grabbed = False
        while not suitcase_grabbed:
            pass

