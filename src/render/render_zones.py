import pygame
import os
from src.models.ClassZone import StartZone, EndZone, PriorityZone, RestrictedZone, BlockedZone


class Visualizer:
    def __init__(self, algo):
        pygame.init()
        self.algo = algo
        self.width, self.height = 2400, 1400
        self.screen = pygame.display.set_mode((self.width, self.height))
        self._setup_grid()
        self.move_index = 0
        self.move_timer = 0
        self.move_delay = 1000
        self.assets = self._load()
        self.clock = pygame.time.Clock()

    def _setup_grid(self):
        """Calcula posiciones lógicas basándose en las zonas del JSON."""
        self.cols = max(z.x_y[0] for z in self.algo.data.zones) + 1
        self.rows = max(z.x_y[1] for z in self.algo.data.zones) + 1
        self.tile_size = int(min((self.width * 0.8) // self.cols, (self.height * 0.8) // self.rows))
        self.off_x = (self.width - (self.cols * self.tile_size)) // 2
        self.off_y = (self.height - (self.rows * self.tile_size)) // 2

    def _load(self):
        p = os.path.join(os.path.dirname(__file__), "..", "assents")
        size = int(self.tile_size * 0.7)
        return {
            "bg":  self._img(p, "fondo.png", (self.width, self.height)),
            "pol": self._img(p, "policia.png", (size, size)),
            "start": self._img(p, "start_zone.png", (size, size)),
            "end": self._img(p, "end_zone.png", (size, size)),
            "prio": self._img(p, "priority.png", (size, size)),
            "restrict": self._img(p, "restricted.png", (size, size)),
            "block": self._img(p, "block.png", (size, size)),
            "dron": self._img(p, "dron.png", (size, size))
        }

    def _img(self, folder, name, size):
        try:
            img = pygame.image.load(os.path.join(folder, name)).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            surf = pygame.Surface(size); surf.fill((255, 0, 255))
            return surf

    def _draw_connections(self):
        color_borde = (30, 30, 30)
        color_relleno = (120, 120, 120)
        zones_by_name = {z.name: z for z in self.algo.data.zones}
        for z in self.algo.data.zones:
            x1 = (z.x_y[0] * self.tile_size) + self.off_x + (self.tile_size // 2)
            y1 = (z.x_y[1] * self.tile_size) + self.off_y + (self.tile_size // 2)
            for conn in z.connection:
                base_gordo = self.tile_size * 0.15
                ancho = int(base_gordo + (conn.capacity * 2))
                n1, n2 = conn.nodes
                neighbor_name = n2 if n1 == z.name else n1
                neighbor = zones_by_name.get(neighbor_name)
                if neighbor:
                    x2 = (neighbor.x_y[0] * self.tile_size) + self.off_x + (self.tile_size // 2)
                    y2 = (neighbor.x_y[1] * self.tile_size) + self.off_y + (self.tile_size // 2)
                    pygame.draw.line(self.screen, color_borde, (x1, y1), (x2, y2), ancho + 6)
                    pygame.draw.line(self.screen, color_relleno, (x1, y1), (x2, y2), ancho)

    def _draw_drones(self, zones_by_name):
        """Calcula la posición fluida y dibuja los drones."""
        lerp_speed = 0.1
        for d in self.algo.data.drons:
            target_zone = zones_by_name.get(d.current_zone)
            if not target_zone: continue
            tx = (target_zone.x_y[0] * self.tile_size) + self.off_x + (self.tile_size // 2)
            ty = (target_zone.x_y[1] * self.tile_size) + self.off_y + (self.tile_size // 2)
            target_x = tx - (self.assets["dron"].get_width() // 2)
            target_y = ty - (self.assets["dron"].get_height() // 2)
            if not hasattr(d, 'real_x'):
                d.real_x, d.real_y = target_x, target_y
            d.real_x += (target_x - d.real_x) * lerp_speed
            d.real_y += (target_y - d.real_y) * lerp_speed
            self.screen.blit(self.assets["dron"], (d.real_x, d.real_y))

    def _draw(self):
        self.screen.blit(self.assets["bg"], (0, 0))
        zones_by_name = {z.name: z for z in self.algo.data.zones}
        self._draw_connections()
        for z in self.algo.data.zones:
            zx = (z.x_y[0] * self.tile_size) + self.off_x
            zy = (z.x_y[1] * self.tile_size) + self.off_y
            if isinstance(z, StartZone):
                img = self.assets["start"]
            elif isinstance(z, EndZone):
                img = self.assets["end"]
            elif isinstance(z, PriorityZone):
                img = self.assets["prio"]
            elif isinstance(z, RestrictedZone):
                img = self.assets["restrict"]
            elif isinstance(z, BlockedZone):
                img = self.assets["block"]
            else:
                img = self.assets["pol"]
            ix = zx + (self.tile_size - img.get_width()) // 2
            iy = zy + (self.tile_size - img.get_height()) // 2
            self.screen.blit(img, (ix, iy))
        self._draw_drones(zones_by_name)

    def _update_movements(self, zones_by_name):
        """Procesa todos los movimientos de un 'bloque' de golpe."""
        if self.move_index >= len(self.algo.moves):
            return
        all_arrived = True
        for d in self.algo.data.drons:
            if hasattr(d, 'real_x') and d.current_zone:
                target_zone = zones_by_name.get(d.current_zone)
                if target_zone:
                    tx = (target_zone.x_y[0] * self.tile_size) + self.off_x + (self.tile_size // 2)
                    ty = (target_zone.x_y[1] * self.tile_size) + self.off_y + (self.tile_size // 2)
                    target_x = tx - (self.assets["dron"].get_width() // 2)
                    target_y = ty - (self.assets["dron"].get_height() // 2)
                    dist = abs(d.real_x - target_x) + abs(d.real_y - target_y)
                    if dist > 5:
                        all_arrived = False
                        break
        now = pygame.time.get_ticks()
        if all_arrived and (now - self.move_timer > self.move_delay):
            drones_movidos_en_este_turno = set()
            while self.move_index < len(self.algo.moves):
                current_move = self.algo.moves[self.move_index]
                try:
                    raw_move = current_move.split(": ")[-1] if ": " in current_move else current_move
                    dron_id, target_zone_name = raw_move.split("-")
                    if dron_id in drones_movidos_en_este_turno:
                        break
                    for d in self.algo.data.drons:
                        if str(d.id) == dron_id or f"D{d.id}" == dron_id:
                            d.current_zone = target_zone_name
                            drones_movidos_en_este_turno.add(dron_id)
                            break
                except ValueError:
                    pass
                self.move_index += 1
            self.move_timer = now

    def main_loop(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
            zones_by_name = {z.name: z for z in self.algo.data.zones}
            self._update_movements(zones_by_name)
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)
