from typing import List, Dict, Any, Optional
from src.models.ClassZone import Zone, NormalZone, PriorityZone, \
      RestrictedZone, BlockedZone, StartZone, EndZone
from src.models.Dron import Dron
from src.models.Connections import Connection


class FlyinData:
    def __init__(self) -> None:
        self.zones: List[Zone] = []
        self.drons: List[Dron] = []
        self.connections: List[Connection] = []
        self.map_zones: Dict[Zone, Zone] = {}

    def _create_drons(self, id_n: int) -> Dron:
        return Dron(id_n)

    def _select_connection(self, tunnel: Any) -> Connection:
        return Connection(tunnel.name1, tunnel.name2, tunnel.max_link_capacity)

    def _select_zone(self, hub_data: Any) -> Zone:
        params = {
            "typ": hub_data.zone,
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

    def get_connection(
            self, zone_a: Zone, zone_b: Zone
            ) -> Optional[Connection]:
        if not zone_a or not zone_b:
            return None
        for conn in zone_a.connection:
            nombres_en_conexion = [
                node.name
                if hasattr(node, 'name')
                else node
                for node in conn.nodes
            ]
            if zone_b.name in nombres_en_conexion:
                return conn
        return None

    def _append_zones_drons_connections(self, data: List[Any]) -> None:
        num_drones = int(data[0]) if isinstance(data[0], (int, str)) else 0
        for i in range(num_drones):
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
                if zone.name in connect.nodes:
                    if connect not in zone.connection:
                        zone.connection.append(connect)
                connect.map_zones.update(self.map_zones)
