from typing import List, Optional, Any
from src.models.ClassZone import Zone
from src.models.Connections import Connection


class Dron:
    def __init__(self, id_nb: int) -> None:
        self.id: int = id_nb
        self.path: List[Any] = []
        self.current_zone: Optional[Any] = None
        self.end_path: bool = False
        self.is_in_transit: bool = False
        self.target_zone: Optional[Any] = None
        self.active_connection: Optional[Any] = None

    def check_next_step(self) -> Optional[Any]:
        if self.path:
            return self.path[0]
        return None

    def move_way(self, next_zone: Zone, conn: Connection) -> None:
        if self.current_zone:
            self.current_zone.current_drones.remove(self)
        self.active_connection = conn
        if self in next_zone.reserved_zone:
            next_zone.reserved_zone.remove(self)
        if next_zone.typ.value == "restricted":
            self.is_in_transit = True
            self.target_zone = next_zone
            self.current_zone = None
        else:
            self.current_zone = next_zone
            next_zone.current_drones.append(self)
        if self.path and self.path[0] == next_zone:
            self.path.pop(0)
