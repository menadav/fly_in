from typing import Any
from src.models.ClassZone import NormalZone, PriorityZone, RestrictedZone, BlockedZone, StartZone, EndZone
from src.models.Dron import Dron


class ManagerZone:
    def __init__(self) -> None:
        self.zones = []
        self.drons = []
        self.connections = []
        self.zones_dict = {}

    def _append_zones_drons_connections(self, data) -> None:
        for i in range(data[0]):
            dron = self._create_drons(i)
            self.drons.append(dron)
        for item in data:
            if hasattr(item, 'x'):
                nueva_zona = self._select_zone(item)
                self.zones.append(nueva_zona)
                self.zones_dict[item.name] = nueva_zona

    def _select_zone(self, hub_data):
        params = {
            "name": hub_data.name,
            "x_y": (hub_data.x, hub_data.y),
            "color": hub_data.color,
            "max_drones": hub_data.max_drones
        }
        if hub_data.type == 'start_hub':
            return StartZone(**params)
        if hub_data.type == 'end_hub':
            return EndZone(**params)
        z_type = hub_data.zone.value if hasattr(hub_data.zone, 'value') else hub_data.zone
        if z_type == 'priority':
            return PriorityZone(**params)
        elif z_type == 'restricted':
            return RestrictedZone(**params)
        elif z_type == 'blocked':
            return BlockedZone(**params)
        return NormalZone(**params)

    def _create_drons(self, id: int) -> Dron:
        return Dron(id)
