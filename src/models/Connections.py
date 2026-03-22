from typing import Dict
from src.models.ClassZone import Zone, StartZone, EndZone


class Connection:
    def __init__(self, zone_1: Zone, zone_2: Zone, capacity: int) -> None:
        self.nodes: tuple[Zone, Zone] = (zone_1, zone_2)
        self.capacity: int = capacity
        self.current_usage: int = 0
        self.map_zones: Dict[Zone, Zone] = {}

    def _check_capacity(self) -> float:
        node1, node2 = self.nodes
        n1: Zone = self.map_zones.get(node1, node1)
        n2: Zone = self.map_zones.get(node2, node2)
        if isinstance(n1, (StartZone, EndZone)):
            cap1 = float('inf')
        else:
            cap1 = float(n1.max_drones)
        if isinstance(n2, (StartZone, EndZone)):
            cap2 = float('inf')
        else:
            cap2 = float(n2.max_drones)
        x = min(cap1, cap2)
        return min(x, self.capacity)

    def occupy(self) -> bool:
        limit = self._check_capacity()
        if self.current_usage < limit:
            self.current_usage += 1
            return True
        else:
            return False

    def release(self) -> None:
        if self.current_usage > 0:
            self.current_usage -= 1
