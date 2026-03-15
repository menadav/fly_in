from src.models.ClassZone import Zone


class Connection:
    def __init__(self, zone_1: Zone, zone_2: Zone, capacity: int):
        self.nodes = (zone_1, zone_2)
        self.capacity = capacity
        self.current_usage = 0
