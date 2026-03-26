from typing import Dict, Tuple, Any, Optional, List
from src.models.ClassZone import Zone, StartZone, EndZone, PriorityZone
from src.models.Dron import Dron


class Algorithm:
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
        dist = distanc[zone]
        prio_type = 0 if isinstance(zone, PriorityZone) else 1
        return (dist, prio_type)

    def _process_dijks(self, dron_actual: Dron) -> List[Zone]:
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
        path: List[Zone] = []
        actual: Optional[Zone] = dest
        while actual is not None:
            path.append(actual)
            actual = father[actual]
        return path[::-1]

    def _start_append(self) -> None:
        if self.start_zone is not None:
            self.start_zone.current_drones.extend(self.data.drons)

    def _reserv_zone(self, dron: Dron) -> None:
        for reserv in dron.path:
            reserv.reserved_zone.append(dron)

    def _check_path_len(self, path: List[Zone]) -> int:
        i = 0
        for x in path:
            if x.typ.value == "restricted":
                i += 2
            else:
                i += 1
        return i

    def simulation_fly(self) -> None:
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
            print(f"Turn {i}- ", end="")
            print(" ".join(moves))
