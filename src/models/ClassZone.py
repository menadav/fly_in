from abc import ABC, abstractmethod


class Zone(ABC):
    def __init__(
            self, name: str, x_y: tuple[int, int], color: str, max_drones: int
            ) -> None:
        self.name = name
        self.x_y = x_y
        self.color = color
        self.max_drones = max_drones
        self.connections = []
        self.neighbor = []
        self.current_drones = []

    @abstractmethod
    def get_movement_cost(self) -> int:
        pass

    @abstractmethod
    def has_capacity(self) -> bool:
        pass


class NormalZone(Zone):

    def get_movement_cost(self) -> int:
        return 1

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class StartZone(NormalZone):
    def __init__(self, name, x_y, color, max_drones) -> None:
        super().__init__(name, x_y, color, max_drones)
        self.role = "START"

    def has_capacity(self) -> bool:
        return True


class EndZone(NormalZone):
    def __init__(self, name, x_y, color, max_drones) -> None:
        super().__init__(name, x_y, color, max_drones)
        self.role = "END"

    def has_capacity(self) -> bool:
        return True


class PriorityZone(Zone):

    def get_movement_cost(self) -> int:
        return 1

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class RestrictedZone(Zone):

    def get_movement_cost(self) -> int:
        return 2

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class BlockedZone(Zone):
    def __init__(self, name, x_y, color, max_drones) -> None:
        super().__init__(name, x_y, color, max_drones)
        self.role = "BLOCKED"

    def get_movement_cost(self) -> int:
        return float('inf')

    def has_capacity(self) -> bool:
        return False
