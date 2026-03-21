import pygame


def run_visual_simulation(self):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    self._start_append()
    # Inicialización de caminos igual que en tu simulation_fly...

    running = True
    while running and len(self.end_zone.current_drones) != len(self.data.drons):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Lógica de actualización (Tu código de simulation_fly) ---
        # Aquí ejecutas UN turno de tu simulación
        self.update_simulation_one_turn()
        screen.fill((30, 30, 30))
        self.draw_network(screen)
        self.draw_drones(screen)
        pygame.display.flip()
        clock.tick(2)
    pygame.quit()