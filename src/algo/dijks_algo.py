from src.models.ClassZone import StartZone, EndZone, PriorityZone


class Algorithm:
    def __init__(self, data) -> None:
        self.data = data
        self.start_zone = next(
            (z for z in self.data.zones if isinstance(z, StartZone)), None
            )
        self.end_zone = next(
            (z for z in self.data.zones if isinstance(z, EndZone)), None
            )

    def _get_priority(self, zone, distanc):
        dist = distanc[zone]
        prio_type = 0 if isinstance(zone, PriorityZone) else 1
        return (dist, prio_type)

    def _process_dijks(self, dron_actual=None):
        distanc = {z: float('inf') for z in self.data.zones}
        father = {z: None for z in self.data.zones}
        next_node = list(self.data.zones)
        distanc[dron_actual.current_zone] = 0

        def wrap_priority(z):
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
                if not neighbor.has_capacity():
                    prio_penality = dron_actual.id * 0.01
                    step_step = 1 + prio_penality
                else:
                    step_step = neighbor.get_movement_cost()
                new_distanc = distanc[node_actual] + step_step
                is_prio = isinstance(neighbor, PriorityZone)
                if new_distanc < distanc[neighbor]:
                    distanc[neighbor] = new_distanc
                    father[neighbor] = node_actual
                elif new_distanc == distanc[neighbor] and is_prio:
                    father[neighbor] = node_actual
        return self._way_path(father, self.end_zone)

    def _way_path(self, father, dest):
        path = []
        actual = dest
        while actual is not None:
            path.append(actual)
            actual = father[actual]
        return path[::-1]

    def _start_append(self) -> None:
        self.start_zone.current_drones.extend(self.data.drons)

    def _reserv_zone(self, dron):
        for reserv in dron.path:
            reserv.reserved_zone.append(dron)

    def _pop_reserv(self, dron):
        for zone in dron.path:
            if dron in zone.reserved_zone:
                zone.reserved_zone.pop(dron)

    def simulation_fly(self) -> None:
        self._start_append()
        for dron in self.data.drons:
            dron.current_zone = self.start_zone
            dron.path = self._process_dijks(dron)
            self._reserv_zone(dron)
        i = 0
        while len(self.end_zone.current_drones) != len(self.data.drons):
            moves = []
            self.data.drons.sort(key=lambda dron: len(dron.path))
            for dron in self.data.drons:
                if dron.current_zone == self.end_zone:
                    continue
                if not dron.movements:
                    dron.movements = True
                    continue
                if dron.path and dron.path[0] == dron.current_zone:
                    dron.path.pop(0)
                next_zone = dron.check_next_step()
                if not next_zone or not next_zone.has_capacity():
                    new_path = self._process_dijks(dron)
                    if len(new_path) < len(dron.path)\
                            or not next_zone.has_capacity():
                        dron.path = new_path
                        self._reserv_zone(dron)
                if next_zone:
                    pathway = self.data.get_connection(
                        dron.current_zone, next_zone
                        )
                    if pathway and next_zone.has_capacity()\
                            and pathway.occupy():
                        dron.move_way(next_zone)
                        moves.append(f"D{dron.id}-{next_zone.name}")
                    else:
                        pass
            for conn in self.data.connections:
                conn.current_usage = 0
            i += 1
            print(f"Turn {i}- ", end="")
            print(" ".join(moves))
