import magicbot
from pyswervedrive.chassis import SwerveChassis


class TeleopSandstorm:
    MODE_NAME = "Teleoperated - Default"
    DEFAULT = True

    robot: magicbot.MagicRobot

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    def on_iteration(self, _time_elapsed):
        self.robot.teleopPeriodic()
