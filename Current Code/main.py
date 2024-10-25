from pyb import Pin, Timer
from Encoder import *
import cotask
from GearboxControl import *
from RobotControl import *
from DcMotor import *
from LimitSwitch import *

if __name__ == '__main__':
    # Common En Pin of Stepper Motors: A15

    # Common Switch Pwr Pin: B13
    switch_pwr_pin = Pin(Pin.cpu.B13, mode=Pin.OUT_PP)
    switch_pwr_pin.high()

    # Back Left Gearbox (#1)
    encoder_bl = Encoder(1, Pin.cpu.A8, Pin.cpu.A9, 5200, 0)
    dc_mot_bl = DcMotor(1, Pin.cpu.A10, Pin.cpu.C10, Pin.cpu.C12, encoder_bl)
    step_mot_bl = StepperMotor(Pin.cpu.A13, Pin.cpu.A14, Pin.cpu.A15)
    lim_switch_bl = LimitSwitch(Pin.cpu.B7)

    dc_mot_bl_flg = task_share.Share('f', name="DC Motor Back Left Flag")
    step_mot_bl_flg = task_share.Share('f', name="Stepper Motor Back Left Flag")
    step_mot_bl_flg.put(1)

    # Back Right Gearbox (#2)
    encoder_br = Encoder(2, Pin.cpu.A2, Pin.cpu.A3, 5200, 0)
    dc_mot_br = DcMotor(2, Pin.cpu.A0, Pin.cpu.C13, Pin.cpu.C14, encoder_br)
    step_mot_br = StepperMotor(Pin.cpu.C15, Pin.cpu.H0, Pin.cpu.A15)
    lim_switch_br = LimitSwitch(Pin.cpu.H1)

    dc_mot_br_flg = task_share.Share('f', name="DC Motor Back Right Flag")
    step_mot_br_flg = task_share.Share('f', name="Stepper Motor Right Left Flag")
    step_mot_br_flg.put(1)

    # Front Left Gearbox (#3)
    encoder_fl = Encoder(3, Pin.cpu.B4, Pin.cpu.B5, 5200, 0)
    dc_mot_fl = DcMotor(3, Pin.cpu.B0, Pin.cpu.C8, Pin.cpu.C6, encoder_fl)
    step_mot_fl = StepperMotor(Pin.cpu.C5, Pin.cpu.A12, Pin.cpu.A15)
    lim_switch_fl = LimitSwitch(Pin.cpu.C0)

    dc_mot_fl_flg = task_share.Share('f', name="DC Motor Front Left Flag")
    step_mot_fl_flg = task_share.Share('f', name="Stepper Motor Front Left Flag")
    step_mot_fl_flg.put(1)

    # Front Right Gearbox (#4)
    encoder_fr = Encoder(4, Pin.cpu.B8, Pin.cpu.B9, 5200, 0)
    dc_mot_fr = DcMotor(4, Pin.cpu.B6, Pin.cpu.B11, Pin.cpu.B2, encoder_fr)
    step_mot_fr = StepperMotor(Pin.cpu.B1, Pin.cpu.B15, Pin.cpu.A15)
    lim_switch_fr = LimitSwitch(Pin.cpu.B14)

    dc_mot_fr_flg = task_share.Share('f', name="DC Motor Front Right Flag")
    step_mot_fr_flg = task_share.Share('f', name="Stepper Motor Front Right Flag")
    step_mot_fr_flg.put(1)

    # Robot Control Task
    task0 = cotask.Task(TaskRobotControl(dc_mot_bl_flg, step_mot_bl_flg,
                                         dc_mot_br_flg, step_mot_br_flg,
                                         dc_mot_fl_flg, step_mot_fl_flg,
                                         dc_mot_fr_flg, step_mot_fr_flg).run,
                        "Task 0: Robot Control", priority=1, period=10)

    # Back Left Gearbox Control Task
    task1 = cotask.Task(TaskGearboxControl(dc_mot_bl_flg, step_mot_bl_flg,dc_mot_bl, step_mot_bl, lim_switch_bl).run,
                        "Task 1: Back Left Gearbox", priority=1, period=5)

    # Back Right Gearbox Control Task
    task2 = cotask.Task(TaskGearboxControl(dc_mot_br_flg, step_mot_br_flg, dc_mot_br, step_mot_br, lim_switch_br).run,
                        "Task 2: Back Right Gearbox", priority=1, period=5)

    # Front Left Gearbox Control Task
    task3 = cotask.Task(TaskGearboxControl(dc_mot_fl_flg, step_mot_fl_flg, dc_mot_fl, step_mot_fl, lim_switch_fl).run,
                        "Task 3: Front Left Gearbox", priority=1, period=5)

    # Front Right Gearbox Control Task
    task4 = cotask.Task(TaskGearboxControl(dc_mot_fr_flg, step_mot_fr_flg, dc_mot_fr, step_mot_fr, lim_switch_fr).run,
                        "Task 4: Front Right Gearbox", priority=1, period=5)

    # Adding Tasks to a Task List
    cotask.task_list.append(task0)
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)

    # Run All tasks
    # TODO: Add break from program if key is pressed
    while True:
        cotask.task_list.pri_sched()
