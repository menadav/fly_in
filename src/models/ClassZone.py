from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from src.models.ZoneConfig import ZoneType
if TYPE_CHECKING:
    from src.models.Connections import Connection
    from src.models.Dron import Dron


class Zone(ABC):
    """
    Abstract base class representing a physical area in the network.

    Defines the interface for movement costs and capacity management that
    specific zone types must implement.
    """
    def __init__(
            self, typ: ZoneType, name: str, x_y: tuple[int, int],
            color: str, max_drones: int
            ) -> None:
        self.typ = typ
        self.name = name
        self.x_y = x_y
        self.color = color
        self.max_drones = max_drones
        self.connection: list['Connection'] = []
        self.current_drones: list['Dron'] = []
        self.reserved_zone: list['Dron'] = []

    @abstractmethod
    def get_movement_cost(self) -> float:
        """Calculates the cost in turns to enter this zone."""
        pass

    @abstractmethod
    def has_capacity(self) -> bool:
        """Checks if a drone can currently enter the zone."""
        pass


class NormalZone(Zone):

    def get_movement_cost(self) -> float:
        flow = len(self.current_drones) + len(self.reserved_zone)
        cost = flow / self.max_drones
        return 1 + (cost ** 4)

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class StartZone(NormalZone):
    def __init__(
            self, typ: ZoneType, name: str, x_y: tuple[int, int],
            color: str, max_drones: int
            ) -> None:
        super().__init__(typ, name, x_y, color, max_drones)
        self.role = "START"

    def has_capacity(self) -> bool:
        """Start zones never block drones from starting."""
        return True


class EndZone(NormalZone):
    def __init__(
            self, typ: ZoneType, name: str, x_y: tuple[int, int],
            color: str, max_drones: int
            ) -> None:
        super().__init__(typ, name, x_y, color, max_drones)
        self.role = "END"

    def has_capacity(self) -> bool:
        """END zones never block drones from starting."""
        return True


class PriorityZone(Zone):

    def get_movement_cost(self) -> float:
        flow = len(self.current_drones) + len(self.reserved_zone)
        cost = flow / self.max_drones
        return 1 + (cost ** 4)

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class RestrictedZone(Zone):

    def get_movement_cost(self) -> float:
        flow = len(self.current_drones) + len(self.reserved_zone)
        cost = flow / self.max_drones
        return 2 + (cost ** 4)

    def has_capacity(self) -> bool:
        return len(self.current_drones) < self.max_drones


class BlockedZone(Zone):

    def get_movement_cost(self) -> float:
        return float('inf')

    def has_capacity(self) -> bool:
        return False
