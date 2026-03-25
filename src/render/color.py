from src.models.ZoneConfig import HubColor


class ColorPalette:
    _RGB_MAP = {
        HubColor.NONE:     (150, 150, 150),
        HubColor.RED:      (255, 0, 0),
        HubColor.BLUE:     (0, 0, 255),
        HubColor.GREEN:    (0, 255, 0),
        HubColor.YELLOW:   (255, 255, 0),
        HubColor.GRAY:     (100, 100, 100),
        HubColor.ORANGE:   (255, 165, 0),
        HubColor.CYAN:     (0, 255, 255),
        HubColor.PURPLE:   (128, 0, 128),
        HubColor.BROWN:    (139, 69, 19),
        HubColor.LIME:     (50, 205, 50),
        HubColor.MAGENTA:  (255, 0, 255),
        HubColor.GOLD:     (212, 175, 55),
        HubColor.BLACK:    (0, 0, 0),
        HubColor.MAROON:   (128, 0, 0),
        HubColor.DARKRED:  (139, 0, 0),
        HubColor.VIOLET:   (238, 130, 238),
        HubColor.CRIMSON:  (220, 20, 60),
    }

    @staticmethod
    def get_rgb(hub_color):
        """Devuelve el color RGB. Si es RAINBOW, genera uno animado."""
        if hub_color == HubColor.RAINBOW:
            return "RAINBOW_SIG"
        return ColorPalette._RGB_MAP.get(hub_color, (200, 200, 200))

    @staticmethod
    def get_all_colors():
        """Devuelve todos los colores disponibles (útil para debug)."""
        return ColorPalette._RGB_MAP.keys()
