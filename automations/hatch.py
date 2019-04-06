import math

from magicbot import StateMachine, state

from components.hatch import Hatch
from pyswervedrive.chassis import SwerveChassis


class HatchAutomation(StateMachine):

    chassis: SwerveChassis
    hatch: Hatch

    def __init__(self):
        super().__init__()
        self.fired_position = 0, 0

    def grab(self):
        self.hatch.retract()
        self.hatch.extend_fingers()
        self.hatch.has_hatch = True

    def outake(self, force=False):
        if force:
            self.engage("outaking_forceful", force=True)
        else:
            self.engage("outaking", force=True)

    @state(must_finish=True)
    def outaking_forceful(self, state_tm, initial_call):
        if initial_call:
            self.hatch.retract_fingers()
        if state_tm > 0.5:
            self.hatch.punch()
            self.next_state("retract")

    @state
    def retract(self):
        self.hatch.retract()
        self.done()

    @state(first=True, must_finish=True)
    def outaking(self, state_tm, initial_call):
        if initial_call:
            self.hatch.retract_fingers()
        if state_tm > 0.5:
            self.hatch.punch()
            self.next_state("retract_after_move")

    @state(must_finish=True)
    def retract_after_move(self, initial_call, state_tm):
        """
        Ensure we have moved away before we retract punchers.
        """
        self.hatch.retract()
        self.done()
