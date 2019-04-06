import enum
import math

import ctre
import rev
import wpilib

from components.vision import Vision

GEAR_RATIO = (7/9) * 7 * 5 * 84 / 50


class Height(enum.Enum):
    FLOOR = 0.313 * GEAR_RATIO
    CARGO_SHIP = 0
    LOADING_STATION = 0


class CargoManipulator:

    vision: Vision

    arm_motor: rev.CANSparkMax
    intake_motor: ctre.VictorSPX

    intake_switch: wpilib.DigitalInput

    INTAKE_SPEED = -1
    SLOW_INTAKE_SPEED = -0.4
    OUTTAKE_SPEED = 1.0

    def __init__(self):
        self.intake_motor_output = 0.0
        self.set_not_moving()

    def setup(self) -> None:
        self.arm_motor.setIdleMode(rev.IdleMode.kBrake)
        self.arm_motor.setInverted(False)
        # self.arm_motor.setSmartCurrentLimit(10)

        self.intake_motor.setNeutralMode(ctre.NeutralMode.Brake)

        self.encoder = self.arm_motor.getEncoder()

        self.pid_controller = self.arm_motor.getPIDController()
        self.pid_controller.setP(5e-4)
        self.pid_controller.setI(1e-6)
        self.pid_controller.setD(0)
        self.pid_controller.setIZone(0)
        self.pid_controller.setFF(1 / 5675)
        self.pid_controller.setOutputRange(-1, 1)
        self.pid_controller.setSmartMotionMaxVelocity(800)  # rpm
        self.pid_controller.setSmartMotionMaxAccel(600)  # rpm/s
        self.pid_controller.setSmartMotionAllowedClosedLoopError(0)
        self.pid_controller.setOutputRange(-1, 1)

        self.top_limit_switch = self.arm_motor.getReverseLimitSwitch(
                rev.LimitSwitchPolarity.kNormallyOpen
                )
        self.bottom_limit_switch = self.arm_motor.getForwardLimitSwitch(
                rev.LimitSwitchPolarity.kNormallyOpen
                )
        self.top_limit_switch.enableLimitSwitch(True)
        self.bottom_limit_switch.enableLimitSwitch(True)

        self.setpoint = Height.LOADING_STATION.value
        self.tolerance = 0.1
        self.has_cargo = False

        self.set_not_moving()

    def execute(self) -> None:
        if self.top_limit_switch.get() and not self.moving_down:
            self.encoder.setPosition(Height.LOADING_STATION.value)
        if self.bottom_limit_switch.get() and not self.moving_up:
            self.encoder.setPosition(Height.FLOOR.value)

        self.intake_motor.set(ctre.ControlMode.PercentOutput, self.intake_motor_output)
        self.pid_controller.setReference(self.setpoint, rev.ControlType.kSmartMotion)

        if self.is_contained():
            self.has_cargo = True
            self.vision.use_cargo()

    def at_height(self, desired_height) -> bool:
        return abs(desired_height.value - self.encoder.getPosition()) <= self.tolerance

    def move_to(self, height: Height) -> None:
        """Move arm to specified height.

        Args:
            height: Height to move arm to
        """
        self.setpoint = height.value
        self.logger.info(f"cargo move_to {self.setpoint}")

    def set_moving_down(self):
        self.moving_down = True
        self.moving_up = False

    def set_moving_up(self):
        self.moving_down = False
        self.moving_up = True

    def set_not_moving(self):
        self.moving_down = False
        self.moving_up = False

    def on_disable(self) -> None:
        self.intake_motor.set(ctre.ControlMode.PercentOutput, 0)
        self.arm_motor.set(0)

    def on_enable(self) -> None:
        self.setpoint = self.encoder.getPosition()
        self.set_not_moving()

    def intake(self) -> None:
        self.intake_motor_output = self.INTAKE_SPEED

    def outtake(self) -> None:
        self.has_cargo = False
        self.intake_motor_output = self.OUTTAKE_SPEED

    def slow_intake(self) -> None:
        self.intake_motor_output = self.SLOW_INTAKE_SPEED

    def stop(self) -> None:
        self.intake_motor_output = 0

    def is_contained(self) -> bool:
        return not self.intake_switch.get()
