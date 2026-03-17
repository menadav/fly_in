from src.models.ClassZone import Zone


class Connection:
    def __init__(self, zone_1: Zone, zone_2: Zone, capacity: int):
        self.nodes = (zone_1, zone_2)
        self.capacity = capacity
        self.current_usage = 0

    def occupy(self) -> bool:
        if self.current_usage < self.capacity:
            self.current_usage += 1
            return True
        else:
            return False

    def release(self) -> None:
        if self.current_usage > 0:
            self.current_usage -= 1
