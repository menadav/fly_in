from typing import Union, Tuple
from src.models.ZoneConfig import HubColor


class ColorPalette:
    """
    Utility class that maps simulation hub colors to RGB values.

    This class serves as a lookup table for the visualizer, ensuring that
    each 'HubColor' enum value corresponds to a specific color on the
    graphical interface. It also supports dynamic effects like rainbow cycling.

    Attributes:
        _RGB_MAP (dict): Private mapping of HubColor enums to (R, G, B) tuples.
    """
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
    def get_rgb(hub_color: HubColor) -> Union[Tuple[int, int, int], str]:
        """
        Retrieves the RGB representation of a given HubColor.

        Args:
            hub_color (HubColor): The enum value representing the hub's color.

        Returns:
            Union[Tuple[int, int, int], str]:
                - A tuple of three integers (0-255) for static colors.
                - The string "RAINBOW_SIG" if the color is
                meant to be animated.
                - A default light-gray tuple (200, 200, 200) if the
                color is not found.
        """
        if hub_color == HubColor.RAINBOW:
            return "RAINBOW_SIG"
        return ColorPalette._RGB_MAP.get(hub_color, (200, 200, 200))
