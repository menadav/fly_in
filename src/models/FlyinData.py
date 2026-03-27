from typing import List, Dict, Any, Optional
from src.models.ClassZone import Zone, NormalZone, PriorityZone, \
      RestrictedZone, BlockedZone, StartZone, EndZone
from src.models.Dron import Dron
from src.models.Connections import Connection


class FlyinData:
    """
    Orchestrates the creation and mapping of the simulation environment.

    This class acts as a factory and container for drones, zones, and
    their interconnections, providing helper methods to retrieve
    network topology information.
    """
    def __init__(self) -> None:
        """Initializes an empty FlyinData environment."""
        self.zones: List[Zone] = []
        self.drons: List[Dron] = []
        self.connections: List[Connection] = []
        self.map_zones: Dict[Zone, Zone] = {}

    def _create_drons(self, id_n: int) -> Dron:
        """
        Factory method to create a new drone instance.
        """
        return Dron(id_n)

    def _select_connection(self, tunnel: Any) -> Connection:
        """
        Factory method to create a connection between two hubs.
        """
        return Connection(tunnel.name1, tunnel.name2, tunnel.max_link_capacity)

    def _select_zone(self, hub_data: Any) -> Zone:
        """
        Determines the specific Zone subclass to instantiate based on metadata.

        Args:
            hub_data (Any): Raw zone data containing type, coordinates,
            and metadata.

        Returns:
            Zone: An instance of StartZone, EndZone, PriorityZone,
            RestrictedZone,
            BlockedZone, or NormalZone.
        """
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
        """
        Retrieves the connection object that links two specific zones.

        Args:
            zone_a (Zone): The starting zone object.
            zone_b (Zone): The target zone object.

        Returns:
            Optional[Connection]: The Connection object if it exists,
            otherwise None.
        """
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
        """
        Processes a list of raw data objects to populate the simulation
        environment.

        This method performs three main tasks:
        1. Instantiates the total number of drones.
        2. Creates and maps all hubs (zones).
        3. Sets up connections and links them to their respective zones.
        Args:
            data (List[Any]): A mixed list containing the drone count,
                              hub definitions, and connection definitions.
        """
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
