from typing import Dict, Tuple, Any, Optional, List
from src.models.ClassZone import Zone, StartZone, EndZone, PriorityZone
from src.models.Dron import Dron


class Algorithm:
    """
    The central simulation engine using a dynamic Dijkstra approach.

    This class coordinates the movement of all drones, recalculating paths
    based on network congestion and managing turn-based state transitions
    (transit, occupancy, and link capacity).
    """
    def __init__(self, data: Any) -> None:
        self.data = data
        self.moves: list[list[str]] = []
        self.start_zone: Optional[StartZone] = next(
            (z for z in self.data.zones if isinstance(z, StartZone)), None
            )
        self.end_zone: Optional[EndZone] = next(
            (z for z in self.data.zones if isinstance(z, EndZone)), None
            )

    def _get_priority(
            self, zone: Zone, distanc: Dict[Zone, float]
            ) -> Tuple[float, int]:
        """
        Calculates a priority tuple for Dijkstra's node selection.

        Args:
            zone (Zone): The hub to evaluate.
            distanc (Dict[Zone, float]): Current distance table.

        Returns:
            Tuple[float, int]: (Distance, Priority flag), where priority hubs
                               have a flag of 0 to be selected first.
        """
        dist = distanc[zone]
        prio_type = 0 if isinstance(zone, PriorityZone) else 1
        return (dist, prio_type)

    def _process_dijks(self, dron_actual: Dron) -> List[Zone]:
        """
        Calculates the optimal path for a specific drone using Dijkstra.

        The algorithm uses the dynamic cost from each zone, which increases
        as more drones occupy or reserve that area.

        Args:
            dron_actual (Dron): The drone requiring a path.

        Returns:
            List[Zone]: An ordered list of Zone objects from current to end.
        """
        distanc: Dict[Zone, float] = {z: float('inf') for z in self.data.zones}
        father: Dict[Zone, Optional[Zone]] = {z: None for z in self.data.zones}
        next_node: List[Zone] = list(self.data.zones)
        curr = dron_actual.current_zone
        if curr is not None:
            distanc[curr] = 0
        else:
            return []

        def wrap_priority(z: Zone) -> Tuple[float, int]:
            return self._get_priority(z, distanc)
        while next_node:
            node_actual = min(next_node, key=wrap_priority)
            if distanc[node_actual] == float('inf'):
                break
            if node_actual == self.end_zone:
                break
            next_node.remove(node_actual)
            for conexion in node_actual.connection:
                zone_neighbor = conexion.nodes[0]\
                    if conexion.nodes[1] == node_actual.name\
                    else conexion.nodes[1]
                neighbor = next(
                    z for z in self.data.zones if z.name == zone_neighbor
                    )
                step_step = neighbor.get_movement_cost()
                new_distanc = distanc[node_actual] + step_step
                is_prio = isinstance(neighbor, PriorityZone)
                if new_distanc < distanc[neighbor]:
                    distanc[neighbor] = new_distanc
                    father[neighbor] = node_actual
                elif new_distanc == distanc[neighbor] and is_prio:
                    father[neighbor] = node_actual
        if self.end_zone:
            return self._way_path(father, self.end_zone)
        return []

    def _way_path(
            self, father: Dict[Zone, Optional[Zone]], dest: Zone
            ) -> List[Zone]:
        """
        Reconstructs the path from the 'father' dictionary.

        Args:
            father (Dict): Mapping of zones to their predecessors.
            dest (Zone): Target destination zone.

        Returns:
            List[Zone]: Reconstructed path from start to finish.
        """
        path: List[Zone] = []
        actual: Optional[Zone] = dest
        while actual is not None:
            path.append(actual)
            actual = father[actual]
        return path[::-1]

    def _start_append(self) -> None:
        """Adds all drones to the starting zone's occupancy list."""
        if self.start_zone is not None:
            self.start_zone.current_drones.extend(self.data.drons)

    def _reserv_zone(self, dron: Dron) -> None:
        """
        Registers a drone in the reservation lists of all
        zones in its path.
        """
        for reserv in dron.path:
            reserv.reserved_zone.append(dron)

    def _check_path_len(self, path: List[Zone]) -> int:
        """
        Calculates the estimated turn duration of a path.

        Args:
            path (List[Zone]): The route to evaluate.

        Returns:
            int: Total turns required, accounting for
            Restricted zones (2 turns).
        """
        i = 0
        for x in path:
            if x.typ.value == "restricted":
                i += 2
            else:
                i += 1
        return i

    def simulation_fly(self) -> None:
        """
        Executes the main simulation loop.

        This method iterates turn-by-turn until all drones reach the end zone.
        It handles:
        1. Drone arrivals from transit.
        2. Dynamic path recalculation if better routes appear.
        3. Movement execution and connection occupancy.
        4. Link capacity releases.
        """
        self._start_append()
        if self.start_zone is None or self.end_zone is None:
            return
        for dron in self.data.drons:
            dron.current_zone = self.start_zone
            dron.path = self._process_dijks(dron)
            self._reserv_zone(dron)
        i = 0
        while len(self.end_zone.current_drones) != len(self.data.drons):
            moves = []
            self.data.drons.sort(key=lambda dron: len(dron.path))
            blocks = [
                d.active_connection
                for d in self.data.drons
                if d.is_in_transit
            ]
            for dron in self.data.drons:
                if dron.current_zone == self.end_zone:
                    continue
                if dron.is_in_transit is True:
                    dron.current_zone = dron.target_zone
                    dron.current_zone.current_drones.append(dron)
                    dron.is_in_transit = False
                    moves.append(f"D{dron.id}-{dron.target_zone.name}")
                    continue
                if dron.path and dron.path[0] == dron.current_zone:
                    dron.path.pop(0)
                next_zone = dron.check_next_step()
                if not next_zone or not next_zone.has_capacity():
                    new_path = self._process_dijks(dron)
                    x = self._check_path_len(new_path)
                    y = self._check_path_len(dron.path)
                    if x < y:
                        dron.path = new_path
                        self._reserv_zone(dron)
                if next_zone:
                    pathway = self.data.get_connection(
                        dron.current_zone, next_zone
                        )
                    if pathway and next_zone.has_capacity()\
                            and pathway.occupy():
                        dron.move_way(next_zone, pathway)
                        if dron.is_in_transit:
                            pass
                        else:
                            moves.append(f"D{dron.id}-{next_zone.name}")
                    else:
                        pass
            for conn in self.data.connections:
                if conn not in blocks:
                    conn.current_usage = 0
                else:
                    pass
            i += 1
            self.moves.append(moves)
