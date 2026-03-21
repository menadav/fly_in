from typing import Dict
from src.models.ClassZone import Zone, StartZone, EndZone


class Connection:
    def __init__(self, zone_1: str, zone_2: str, capacity: int):
        self.nodes: tuple[str, str] = (zone_1, zone_2)
        self.capacity: int = capacity
        self.current_usage: int = 0
        self.map_zones: Dict[Zone, Zone] = {}

    def _check_capacity(self) -> float:
        n1, n2 = self.nodes
        n1 = self.map_zones.get(n1)
        n2 = self.map_zones.get(n2)
        cap1 = float('inf') if isinstance(n1, (StartZone, EndZone))\
            else int(n1.max_drones)
        cap2 = float('inf') if isinstance(n2, (StartZone, EndZone))\
            else int(n2.max_drones)
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
