import os
import src.env_config
from typing import Dict, Tuple, Union
from src.models.ClassZone import StartZone, EndZone, PriorityZone, \
        RestrictedZone, BlockedZone, Zone
from src.render.color import ColorPalette as col
from src.algo.dijks_algo import Algorithm
from src.models.ZoneConfig import ZoneType
import pygame
_ = src.env_config


class Visualizer:
    """
    Graphical engine for the drone simulation using Pygame.

    This class handles the rendering of the map, zones, connections, and
    animated drone movements. It translates the turn-based logic of the
    Algorithm into a smooth, time-based visual experience.

    Attributes:
        algo (Algorithm): The algorithm instance containing simulation results.
        width (int): Screen width in pixels.
        height (int): Screen height in pixels.
        screen (pygame.Surface): The main display surface.
        move_index (int): Current turn being visualized.
        move_timer (int): Timestamp of the last turn update.
        move_delay (int): Real-world milliseconds between simulation turns.
        assets (Dict): Dictionary containing loaded and scaled images.
        clock (pygame.time.Clock): Pygame clock to manage frame rate.
    """
    def __init__(self, algo: Algorithm) -> None:

        pygame.init()
        self.algo = algo
        self.width, self.height = 2400, 1400
        self.screen = pygame.display.set_mode((self.width, self.height))
        self._setup_grid()
        self.move_index = 0
        self.move_timer = 0
        self.move_delay = 1000
        self.assets = self._load()
        self.first_moves = [list(turn) for turn in self.algo.moves]
        self.clock = pygame.time.Clock()
        self._spawn_drones_at_start()
        self._optimize_original_moves()

    def _optimize_original_moves(self) -> None:
        """
        Adjusts move data to account for Restricted Zone delays visually.
        This ensures that drones entering a Restricted Zone appear to spend
        two turns in transition as per simulation rules.
        """
        zones_map = {z.name: z for z in self.algo.data.zones}
        moves = self.algo.moves
        for i in range(1, len(moves)):
            current_turn = moves[i]
            previous_turn = moves[i - 1]
            to_move_back = []
            for move_str in current_turn:
                parts = move_str.split('-')
                if len(parts) < 2:
                    continue
                dron_id = parts[0]
                zone_name = parts[1]
                zone_obj = zones_map.get(zone_name)
                is_restricted = isinstance(
                    zone_obj, RestrictedZone
                    ) or getattr(zone_obj, 'typ', None) == ZoneType.RESTRICTED
                if is_restricted:
                    dron_ocupado_antes = any(
                        m.startswith(f"{dron_id}-") for m in previous_turn
                        )
                    if not dron_ocupado_antes:
                        to_move_back.append((move_str, zone_obj))
            for m, z_obj in to_move_back:
                if not isinstance(z_obj, EndZone):
                    pass
                previous_turn.append(m)
                current_turn.remove(m)

    def _spawn_drones_at_start(self) -> None:
        """Positions all drones at the center of the StartZone initially."""
        start_node = next(
            (z for z in self.algo.data.zones if isinstance(z, StartZone)), None
            )
        if not start_node:
            return
        sx = (
            (start_node.x_y[0] - self.min_x) * self.tile_size
            ) + self.off_x + (self.tile_size // 2)
        sy = (
            (start_node.x_y[1] - self.min_y) * self.tile_size
            ) + self.off_y + (self.tile_size // 2)
        d_w = self.assets["dron"].get_width() // 2
        d_h = self.assets["dron"].get_height() // 2
        for d in self.algo.data.drons:
            d.current_zone = start_node
            d.real_x = sx - d_w
            d.real_y = sy - d_h

    def _setup_grid(self) -> None:
        """
        Calculates tile size and offsets to center the map,
        supporting negative coordinates.
        """
        all_x = [z.x_y[0] for z in self.algo.data.zones]
        all_y = [z.x_y[1] for z in self.algo.data.zones]
        self.min_x, self.max_x = min(all_x), max(all_x)
        self.min_y, self.max_y = min(all_y), max(all_y)
        self.cols = self.max_x - self.min_x + 1
        self.rows = self.max_y - self.min_y + 1
        margen_seguridad = 0.5
        self.tile_size = int(min(
            (self.width * margen_seguridad) // self.cols,
            (self.height * margen_seguridad) // self.rows
        ))
        self.off_x = (self.width - (self.cols * self.tile_size)) // 2
        self.off_y = (self.height - (self.rows * self.tile_size)) // 2

    def _load(self) -> Dict[str, pygame.Surface]:
        """Loads and scales all graphical assets."""
        p = os.path.join(os.path.dirname(__file__), "..", "assents")
        size = int(self.tile_size * 0.7)
        b_size = int(self.tile_size * 0.9)
        return {
            "bg":  self._img(p, "fondo.png", (self.width, self.height)),
            "pol": self._img(p, "policia.png", (size, size)),
            "start": self._img(p, "start_zone.png", (size, size)),
            "end": self._img(p, "end_zone.png", (size, size)),
            "prio": self._img(p, "priority.png", (size, size)),
            "restrict": self._img(p, "restricted.png", (size, size)),
            "block": self._img(p, "block.png", (size, size)),
            "dron": self._img(p, "dron.png", (size, size)),
            "rainbow_bg": self._img(p, "rainbow_circle.png", (b_size, b_size))
        }

    def _img(
            self, folder: str, name: str, size: Tuple[int, int]
            ) -> pygame.Surface:
        """Helper to load a single image with error handling."""
        try:
            path = os.path.join(folder, name)
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception as e:
            print(f"[Error] img {name}: {e}")
            surf = pygame.Surface(size)
            surf.fill((255, 0, 255))
            return surf

    def _draw_connections(self) -> None:
        """Renders the links between zones, adjusting thickness by capacity."""
        color_bord = (30, 30, 30)
        color_final = (120, 120, 120)
        zones_by_name = {z.name: z for z in self.algo.data.zones}
        for z in self.algo.data.zones:
            x1 = (
                (z.x_y[0] - self.min_x) * self.tile_size
                ) + self.off_x + (self.tile_size // 2)
            y1 = (
                (z.x_y[1] - self.min_y) * self.tile_size
                ) + self.off_y + (self.tile_size // 2)
            for conn in z.connection:
                base_gordo = self.tile_size * 0.15
                ancho = int(base_gordo + (conn.capacity * 2))
                n1, n2 = conn.nodes
                neighbor_name = n2 if n1 == z.name else n1
                neighbor = zones_by_name.get(neighbor_name)
                if neighbor:
                    x2 = (
                        (neighbor.x_y[0] - self.min_x) * self.tile_size
                        ) + self.off_x + (self.tile_size // 2)
                    y2 = (
                        (neighbor.x_y[1] - self.min_y) * self.tile_size
                        ) + self.off_y + (self.tile_size // 2)
                    pygame.draw.line(
                        self.screen, color_bord, (x1, y1), (x2, y2), ancho + 6
                        )
                    pygame.draw.line(
                        self.screen, color_final, (x1, y1), (x2, y2), ancho
                        )

    def _replace_black_color(
        self,
        image: pygame.Surface,
        new_color: Union[pygame.Color, Tuple[int, int, int], str]
    ) -> pygame.Surface:
        """Colors a grayscale asset using a provided color."""
        if isinstance(new_color, str):
            return image
        mask = pygame.mask.from_surface(image)
        return mask.to_surface(setcolor=new_color, unsetcolor=(0, 0, 0, 0))

    def _draw(self) -> None:
        """Main draw call: background, connections, zones, and drones."""
        self.screen.blit(self.assets["bg"], (0, 0))
        zones_by_name = {z.name: z for z in self.algo.data.zones}
        self._draw_connections()
        for z in self.algo.data.zones:
            zx = ((z.x_y[0] - self.min_x) * self.tile_size) + self.off_x
            zy = ((z.x_y[1] - self.min_y) * self.tile_size) + self.off_y
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
            target_color = col.get_rgb(z.color)
            if target_color == "RAINBOW_SIG":
                r_ix = zx + (
                    self.tile_size - self.assets["rainbow_bg"].get_width()
                    ) // 2
                r_iy = zy + (
                    self.tile_size - self.assets["rainbow_bg"].get_height()
                    ) // 2
                self.screen.blit(self.assets["rainbow_bg"], (r_ix, r_iy))
                ix = zx + (self.tile_size - img.get_width()) // 2
                iy = zy + (self.tile_size - img.get_height()) // 2
                self.screen.blit(img, (ix, iy))
            else:
                img_final = self._replace_black_color(img, target_color)
                ix = zx + (self.tile_size - img_final.get_width()) // 2
                iy = zy + (self.tile_size - img_final.get_height()) // 2
                self.screen.blit(img_final, (ix, iy))
        self._draw_drones(zones_by_name)

    def _draw_drones(self, zones_by_name: Dict[str, Zone]) -> None:
        """Renders drones and updates their interpolated positions."""
        for d in self.algo.data.drons:
            if hasattr(d, 'target_pos') and d.travel_t < 1.0:
                d.travel_t = min(1.0, d.travel_t + getattr(d, 'step', 0.016))
                d.real_x = d.origin_pos[0] + (
                    d.target_pos[0] - d.origin_pos[0]
                    ) * d.travel_t
                d.real_y = d.origin_pos[1] + (
                    d.target_pos[1] - d.origin_pos[1]
                    ) * d.travel_t
            self.screen.blit(self.assets["dron"], (d.real_x, d.real_y))

    def _update_movements(self, zones_by_name: Dict[str, Zone]) -> None:
        """
        Checks if enough time has passed to trigger the next turn's movements.
        """
        now = pygame.time.get_ticks()
        if self.move_index >= len(self.algo.moves):
            if not getattr(self, 'sim_finished', False):
                print("")
                self.sim_finished = True
            return
        if now - self.move_timer <= self.move_delay:
            return
        current_moves = self.first_moves[self.move_index]
        print(f"\nTurn {self.move_index + 1}-", end=" ")
        if not current_moves:
            pass
        else:
            for m_str in current_moves:
                print(f"{m_str}", end=" ")
        for move_str in self.algo.moves[self.move_index]:
            d_id, z_name = move_str.split("-")
            targets = [dr for dr in self.algo.data.drons
                       if f"D{dr.id}" == d_id or str(dr.id) == d_id]
            for d in targets:
                tz = zones_by_name.get(z_name)
                if tz:
                    d.origin_pos = (d.real_x, d.real_y)
                    is_slow = isinstance(tz, RestrictedZone)\
                        or (
                            isinstance(
                                tz, EndZone
                                ) and tz.typ == ZoneType.RESTRICTED
                            )
                    f = 2.0 if is_slow else 1.0
                    d.step = (1000 / 60) / (self.move_delay * f)
                    d.target_pos = (
                        ((
                            tz.x_y[0] - self.min_x
                            ) * self.tile_size) + self.off_x + (
                            self.tile_size // 2
                            ) - (self.assets["dron"].get_width() // 2),
                        ((
                            tz.x_y[1] - self.min_y
                            ) * self.tile_size) + self.off_y + (
                            self.tile_size // 2
                            ) - (self.assets["dron"].get_height() // 2)
                    )
                    d.travel_t = 0.0
        self.move_index += 1
        self.move_timer = now

    def main_loop(self) -> None:
        """
        Main application loop handling events, updates, and rendering.
        """
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE or e.key == pygame.K_q:
                        running = False
            zones_by_name = {z.name: z for z in self.algo.data.zones}
            self._update_movements(zones_by_name)
            self._draw()
            pygame.display.flip()
            self.clock.tick(70)
