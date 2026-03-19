class Dron:
    def __init__(self, id_nb: int) -> None:
        self.id = id_nb
        self.path = []
        self.current_zone = None
        self.movements = True

    def check_next_step(self):
        if self.path:
            return self.path[0]
        return None

    def move_way(self, next_zone) -> None:
        if self.current_zone:
            self.current_zone.current_drones.remove(self)
        next_zone.current_drones.append(self)
        self.current_zone = next_zone
        cost = next_zone.get_movement_cost()
        if cost == 2:
            self.movements = False
        if self.path and self.path[0] == next_zone:
            self.path.pop(0)
