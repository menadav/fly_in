from src.models.ClassZone import NormalZone, PriorityZone, \
      RestrictedZone, BlockedZone, StartZone, EndZone
from src.models.Dron import Dron
from src.models.Connections import Connection


class FlyinData:
    def __init__(self) -> None:
        self.zones = []
        self.drons = []
        self.connections = []
        self.map_zones = {}

    def _create_drons(self, id_n: int) -> Dron:
        return Dron(id_n)

    def _select_connection(self, tunnel):
        return Connection(tunnel.name1, tunnel.name2, tunnel.max_link_capacity)

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
        z_type = hub_data.zone.value if hasattr(hub_data.zone, 'value')\
            else hub_data.zone
        if z_type == 'priority':
            return PriorityZone(**params)
        elif z_type == 'restricted':
            return RestrictedZone(**params)
        elif z_type == 'blocked':
            return BlockedZone(**params)
        return NormalZone(**params)

    def _append_zones_drons_connections(self, data) -> None:
        for i in range(data[0]):
            dron = self._create_drons(i)
            self.drons.append(dron)
        for item in data:
            if hasattr(item, 'x'):
                new_zone = self._select_zone(item)
                self.zones.append(new_zone)
                self.map_zones[item.name] = new_zone
            if hasattr(item, 'max_link_capacity'):
                new_connection = self._select_connection(item)
                self.connections.append(new_connection)
        for zone in self.zones:
            for connect in self.connections:
                x, y = connect.nodes
                if x == zone.name:
                    zone.neighbor.append(y)
                if y == zone.name:
                    zone.neighbor.append(x)
        for zone in self.zones:
            for connect in self.connections:
                if zone.name in connect.nodes and\
                        any(check in connect.nodes for check in zone.neighbor):
                    zone.connections.append(connect)

