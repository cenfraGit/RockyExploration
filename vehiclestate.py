# vehiclestate.py

from typing import Tuple

class VehicleState:
    def __init__(self):
        self.path_points = []
        self.max_points = 2000

    def add_position(self, new_position:Tuple[float, float, float]):
        if len(self.path_points) > self.max_points - 1: # use queue
            self.path_points.pop(0)
        self.path_points.append(list(new_position))