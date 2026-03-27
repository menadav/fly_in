from typing import Dict
from src.models.ClassZone import Zone, StartZone, EndZone


class Connection:
    """
    Represents a physical link between two zones in the simulation network.

    This class manages the traffic capacity between nodes, ensuring that
    drone flow does not exceed the limits of the link itself or the
    connected hubs.
    """
    def __init__(self, zone_1: Zone, zone_2: Zone, capacity: int) -> None:
        self.nodes: tuple[Zone, Zone] = (zone_1, zone_2)
        self.capacity: int = capacity
        self.current_usage: int = 0
        self.map_zones: Dict[Zone, Zone] = {}

    def _check_capacity(self) -> float:
        """
        Calculates the real-time limit of drones that can use this connection.

        The limit is determined by the minimum value between the link's own
        capacity and the capacity of the zones it connects (Start and End
        Zones are treated as having infinite capacity).

        Returns:
            float: The maximum number of drones permitted on this link.
        """
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
        """
        Attempts to register a drone entering the connection.
        Increments the usage count if there is available space based on
        the calculated capacity limit.
        """
        limit = self._check_capacity()
        if self.current_usage < limit:
            self.current_usage += 1
            return True
        else:
            return False

    def release(self) -> None:
        """
        Reduces the current usage count when a drone finishes
        traversing the link.
        """
        if self.current_usage > 0:
            self.current_usage -= 1
